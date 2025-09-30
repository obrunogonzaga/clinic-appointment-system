"""
Service for parsing Excel files containing appointment data.
"""

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, BinaryIO, Dict, List, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, ValidationError

from src.application.services.address_normalization_service import (
    AddressNormalizationService,
)
from src.application.services.document_normalization_service import (
    DocumentNormalizationService,
)
from src.domain.entities.appointment import Appointment, AppointmentOrigin
from src.infrastructure.config import get_settings

# Import CarService for type annotation
if TYPE_CHECKING:
    from src.application.services.car_service import CarService


class ExcelParseResult(BaseModel):
    """Result of Excel parsing operation."""

    success: bool
    appointments: List[Appointment] = []
    errors: List[str] = []
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    cars_created: int = 0  # Number of cars created during import


class ExcelParseError(BaseModel):
    """Error details for a specific row."""

    row_number: int
    error_message: str
    row_data: Dict = {}


class ExcelParserService:
    """
    Service for parsing Excel files with appointment data.

    This service handles the conversion of Excel data into Appointment entities
    with proper validation and error handling.
    """

    # Column mapping from Excel to our domain model
    COLUMN_MAPPING = {
        "Nome da Marca": "nome_marca",
        "Nome da Unidade": "nome_unidade",
        "Nome do Paciente": "nome_paciente",
        "Data/Hora Início Agendamento": "data_hora_agendamento",
        "Status Agendamento": "status_agendamento",
        "Contato(s) do Paciente": "telefone",
        "Observação": "observacoes",
        "Observações": "observacoes",  # Campo específico de observações
        "Nomes dos Exames": "tipo_consulta",
        # Campos de confirmação
        "Canal Confirmação": "canal_confirmacao",
        "Canal de Confirmação": "canal_confirmacao",  # Alternativo
        "Data/Hora Confirmação": "data_hora_confirmacao",
        "Data da Confirmação": "data_confirmacao",  # Alternativo
        "Hora da Confirmação": "hora_confirmacao",  # Alternativo
        # Campos extras tentativos (se existirem nas planilhas)
        "CEP": "cep",
        "Endereço Coleta": "endereco_coleta",
        "Endereço Completo": "endereco_completo",
        "Convênio": "numero_convenio",
        "Numero Convenio": "numero_convenio",
        "Número Convênio": "numero_convenio",
        "Nome do Convênio": "nome_convenio",
        "Nome Convenio": "nome_convenio",
        "Nome Convênio": "nome_convenio",
        "Nr. Carteira": "carteira_convenio",
        "Nr Carteira": "carteira_convenio",
        "Carteira": "carteira_convenio",
    }

    # Status mapping from Excel to our domain model
    STATUS_MAPPING = {
        "pendente": "Pendente",
        "autorição": "Autorização",
        "autorização": "Autorização",
        "autorizacao": "Autorização",
        "cadastrar": "Cadastrar",
        "agendado": "Agendado",
        "confirmado": "Confirmado",
        "coletado": "Coletado",
        "alterar": "Alterar",
        "cancelado": "Cancelado",
        "recoleta": "Recoleta",
        "não confirmado": "Pendente",
        "nao confirmado": "Pendente",
    }

    def __init__(
        self,
        address_service: Optional[AddressNormalizationService] = None,
        car_service: Optional["CarService"] = None,
        document_service: Optional[DocumentNormalizationService] = None,
    ) -> None:
        """Initialize the parser service."""
        self.supported_formats = [".xlsx", ".xls", ".csv"]
        self.address_service = address_service
        self.car_service = car_service
        self.document_service = document_service
        # Importar somente quando "Nome da Sala" iniciar com o padrão
        # AA-AA-AA-AA-AA (ex.: AD-SF-FQ-AC-AV ou AD-SF-FQ-AC-BALTHAZAR)
        # Aceita segmentos de 2 ou mais letras. Texto extra à direita
        # (ex.: "CENTER 3 CARRO 1 - UND84") será preservado.
        self.SALA_PATTERN = re.compile(
            r"^[A-Z]{2,}(?:-[A-Z]{2,}){4}(?:\s+.*)?$"
        )
        self.SALA_EXTRACT_PATTERN = re.compile(
            r"^(?P<sala>[A-Z]{2,}(?:-[A-Z]{2,}){4})(?:\s+(?P<carro>.+))?$"
        )

    async def parse_excel_file(
        self, file_content: BinaryIO, filename: str
    ) -> ExcelParseResult:
        """
        Parse Excel file and convert to Appointment entities.

        Args:
            file_content: Binary content of the Excel file
            filename: Name of the uploaded file

        Returns:
            ExcelParseResult: Result containing parsed appointments and errors
        """
        try:
            # Read Excel file
            df = self._read_excel_file(file_content, filename)

            # Parse appointments
            return await self._parse_dataframe(df)

        except Exception as e:
            return ExcelParseResult(
                success=False,
                errors=[f"Erro ao ler arquivo Excel: {str(e)}"],
                total_rows=0,
            )

    def _read_excel_file(
        self, file_content: BinaryIO, filename: str
    ) -> pd.DataFrame:
        """
        Read Excel file into pandas DataFrame.

        Args:
            file_content: Binary content of the file
            filename: Name of the file

        Returns:
            pd.DataFrame: Parsed Excel data
        """
        # Reset file pointer to beginning
        file_content.seek(0)

        # Determine file format
        if filename.endswith(".csv"):
            df = pd.read_csv(file_content, encoding="utf-8")
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(file_content, engine="openpyxl")
        elif filename.endswith(".xls"):
            # Try openpyxl first (for .xls files that are actually .xlsx)
            try:
                file_content.seek(0)
                df = pd.read_excel(file_content, engine="openpyxl")
            except Exception:
                # Fall back to xlrd for real .xls files
                file_content.seek(0)
                df = pd.read_excel(file_content, engine="xlrd")
        else:
            raise ValueError(f"Formato de arquivo não suportado: {filename}")

        # Basic validation
        if df.empty:
            raise ValueError("Arquivo Excel está vazio")

        # Check if required columns exist
        required_columns = [
            "Nome da Marca",
            "Nome da Unidade",
            "Nome do Paciente",
        ]
        missing_columns = [
            col for col in required_columns if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Colunas obrigatórias não encontradas: "
                + ", ".join(missing_columns)
            )

        return df

    async def _parse_dataframe(self, df: pd.DataFrame) -> ExcelParseResult:
        """
        Parse DataFrame into Appointment entities.

        Args:
            df: Pandas DataFrame with Excel data

        Returns:
            ExcelParseResult: Result with parsed appointments
        """
        appointments = []
        errors = []
        cars_created = 0
        processed_cars = set()  # Track cars already processed
        original_total_rows = len(df)

        # Filtra por padrão do "Nome da Sala" quando a coluna existir.
        # Somente linhas no formato AA-AA-AA-AA-AA devem ser importadas.
        if "Nome da Sala" in df.columns:
            try:
                mask = (
                    df["Nome da Sala"]
                    .astype(str)
                    .str.fullmatch(self.SALA_PATTERN)
                )
                # Algumas versões retornam NaN para valores vazios
                mask = mask.fillna(False)
                df = df[mask]
            except Exception:
                # Se falhar o filtro, não interromper a importação
                pass

        for index, row in df.iterrows():
            try:
                appointment = self._parse_row(row)
                if appointment:
                    # Process car registration if car_service is available
                    car_id = None
                    if appointment.carro and self.car_service:
                        car_id = await self._process_car(
                            appointment.carro, processed_cars
                        )
                        if car_id and appointment.carro not in processed_cars:
                            cars_created += 1
                            processed_cars.add(appointment.carro)

                    # Set car_id in appointment if found/created
                    if car_id:
                        appointment.car_id = car_id

                    appointments.append(appointment)

            except Exception as e:
                errors.append(f"Linha {index + 1}: {str(e)}")

        # Normalizar endereços se o serviço estiver disponível E habilitado
        settings = get_settings()
        if (
            self.address_service
            and appointments
            and settings.address_normalization_enabled
        ):
            appointments = await self._normalize_addresses_batch(appointments)

        # Normalizar documentos se o serviço estiver disponível E habilitado
        if (
            self.document_service
            and appointments
            and settings.address_normalization_enabled  # Reuse the same setting
        ):
            appointments = await self._normalize_documents_batch(appointments)

        return ExcelParseResult(
            success=len(errors) == 0,
            appointments=appointments,
            errors=errors,
            total_rows=original_total_rows,
            valid_rows=len(appointments),
            invalid_rows=len(errors),
            cars_created=cars_created,
        )

    def _parse_row(self, row: pd.Series) -> Optional[Appointment]:
        """
        Parse a single row into an Appointment entity.

        Args:
            row: Pandas Series representing a row

        Returns:
            Optional[Appointment]: Parsed appointment or None if invalid
        """
        try:
            # Extract required fields
            nome_marca = self._clean_string(row.get("Nome da Marca"))
            nome_unidade = self._clean_string(row.get("Nome da Unidade"))
            nome_paciente = self._clean_string(row.get("Nome do Paciente"))

            # Validate required fields
            if not nome_marca or not nome_unidade or not nome_paciente:
                raise ValueError(
                    "Campos obrigatórios em branco "
                    "(Nome da Marca, Nome da Unidade, Nome do Paciente)"
                )

            # Parse date and time
            data_agendamento, hora_agendamento = self._parse_datetime(
                row.get("Data/Hora Início Agendamento")
            )

            # Parse optional fields
            status = self._decide_status(row)
            telefone = self._clean_phone(row.get("Contato(s) do Paciente"))
            # Observações vêm do campo "Observação" da planilha
            observacoes = self._clean_string(row.get("Observação"))
            # Se há campo "Observações" separado, prioriza ele
            if row.get("Observações"):
                observacoes = self._clean_string(row.get("Observações"))

            # Carro vem da extração do campo "Nome da Sala"
            # Formato: AA-BB-CC-DD-NOME_CARRO RESTO - UNIDADE
            # Extrair apenas: NOME_CARRO RESTO
            carro = None
            sala_val = self._clean_string(row.get("Nome da Sala"))
            if sala_val:
                # Remover os primeiros 4 segmentos (AA-BB-CC-DD-)
                # e extrair apenas o 5º segmento + informação do carro
                parts = sala_val.split("-", 4)  # Split em até 4 hífens
                if len(parts) == 5:
                    # parts[4] contém: "NOME_CARRO RESTO - UNIDADE"
                    remaining = parts[4].strip()
                    # Agora extrair apenas até o " - UNIDADE"
                    if " - " in remaining:
                        carro_part = remaining.split(" - ")[0].strip()
                        carro = carro_part if carro_part else None
                    else:
                        carro = remaining
            tipo_consulta = self._clean_string(row.get("Nomes dos Exames"))
            cep = self._clean_string(row.get("CEP"))
            endereco_coleta = self._clean_string(row.get("Endereço Coleta"))
            endereco_completo = self._clean_string(
                row.get("Endereço Completo")
            )

            # Se endereco_completo não existe, usar endereco_coleta como fallback
            if not endereco_completo and endereco_coleta:
                endereco_completo = endereco_coleta

            # Extrair campo de documento do paciente
            documento_completo = self._clean_string(
                row.get("Documento(s) do Paciente")
            )
            numero_convenio = self._clean_string(
                row.get("Convênio")
                or row.get("Numero Convenio")
                or row.get("Número Convênio")
            )
            nome_convenio = self._clean_string(
                row.get("Nome do Convênio")
                or row.get("Nome Convenio")
                or row.get("Nome Convênio")
            )
            carteira_convenio = self._clean_string(
                row.get("Nr. Carteira")
                or row.get("Nr Carteira")
                or row.get("Carteira")
            )
            canal_confirmacao = self._clean_string(
                row.get("Canal Confirmação") or row.get("Canal de Confirmação")
            )

            # Tentar extrair data/hora do campo combinado ou campos separados
            data_conf, hora_conf = self._parse_confirmacao_datetime(
                row.get("Data/Hora Confirmação"),
                row.get("Data da Confirmação"),
                row.get("Hora da Confirmação"),
            )

            # Normalizar endereço se o serviço estiver disponível
            endereco_normalizado = None
            if endereco_completo and self.address_service:
                try:
                    # Note: Este é um parse síncrono, mas a normalização é assíncrona
                    # Para este contexto, vamos pular a normalização durante o parse
                    # e fazer em um passo separado após a criação
                    pass
                except Exception as e:
                    # Log do erro, mas não falha o parse
                    print(f"Erro na normalização de endereço: {e}")

            # Create appointment entity
            appointment = Appointment(
                nome_marca=nome_marca,
                nome_unidade=nome_unidade,
                nome_paciente=nome_paciente,
                data_agendamento=data_agendamento,
                hora_agendamento=hora_agendamento,
                status=status,
                telefone=telefone,
                carro=carro,
                observacoes=observacoes,
                tipo_consulta=tipo_consulta,
                canal_confirmacao=canal_confirmacao,
                data_confirmacao=data_conf,
                hora_confirmacao=hora_conf,
                driver_id=None,
                cep=cep,
                endereco_coleta=endereco_coleta,
                endereco_completo=endereco_completo,
                endereco_normalizado=endereco_normalizado,
                documento_completo=documento_completo,
                documento_normalizado=None,  # Will be set during normalization
                cpf=None,  # Will be extracted during normalization
                rg=None,  # Will be extracted during normalization
                numero_convenio=numero_convenio,
                nome_convenio=nome_convenio,
                carteira_convenio=carteira_convenio,
                origin=AppointmentOrigin.DASA,
            )

            return appointment

        except ValidationError as e:
            error_messages = [
                f"{err['loc'][0]}: {err['msg']}" for err in e.errors()
            ]
            raise ValueError(
                f"Erro de validação - {'; '.join(error_messages)}"
            )
        except Exception as e:
            raise ValueError(f"Erro ao processar linha: {str(e)}")

    def _clean_string(self, value: Any) -> Optional[str]:
        """
        Clean and validate string values.

        Args:
            value: Raw value from Excel

        Returns:
            Optional[str]: Cleaned string or None
        """
        if pd.isna(value) or value is None:
            return None

        cleaned = str(value).strip()
        return cleaned if cleaned else None

    def _clean_phone(self, value: Any) -> Optional[str]:
        """
        Clean and normalize phone number from mixed text.

        Preference order:
        1) Numbers with DDD (10 or 11 digits)
        2) Otherwise, return None (do not fail the row)
        """
        if pd.isna(value) or value is None:
            return None

        import re

        text = str(value).strip()
        # Remove country code formats
        text = text.replace("+55", "").replace("+ 55", "").replace("+  55", "")

        # Find candidate numbers with optional DDD and formatting
        # e.g.: (41) 99945-7777, 41999457777, 41 3333-4444
        pattern = r"(?:\(\d{2}\)\s*|\b\d{2}\s*)?\d{4,5}\s*-?\s*\d{4}"
        matches = re.findall(pattern, text)

        def only_digits(s: str) -> str:
            return re.sub(r"\D", "", s)

        # Normalize and pick the first valid (10 or 11 digits)
        for m in matches:
            digits = only_digits(m)
            # Remove leading 55 if present
            if digits.startswith("55") and len(digits) > 11:
                digits = digits[2:]
            if len(digits) in (10, 11):
                return digits

        # Fallback: look for any contiguous 10-11 digits
        contiguous = re.findall(r"\d{10,11}", only_digits(text))
        if contiguous:
            return contiguous[0]

        # If nothing with DDD was found, ignore shorter numbers
        return None

    def _parse_datetime(self, value: Any) -> Tuple[datetime, str]:
        """
        Parse date/time value from Excel.

        Args:
            value: Raw datetime value from Excel

        Returns:
            Tuple[datetime, str]: Parsed date and time string
        """
        if pd.isna(value) or value is None:
            raise ValueError("Data/hora de agendamento é obrigatória")

        # Handle different datetime formats
        if isinstance(value, datetime):
            # Already a datetime object
            dt = value
        elif isinstance(value, str):
            # Try to parse string formats
            for fmt in [
                "%d/%m/%Y %H:%M",
                "%d/%m/%Y %H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
            ]:
                try:
                    dt = datetime.strptime(value.strip(), fmt)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Formato de data/hora inválido: {value}")
        else:
            raise ValueError(f"Tipo de data/hora não suportado: {type(value)}")

        # Extract date and time
        data_agendamento = dt.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        hora_agendamento = dt.strftime("%H:%M")

        return data_agendamento, hora_agendamento

    def _map_status(self, value: Any) -> str:
        """
        Map status from Excel to our domain model.

        Args:
            value: Raw status value from Excel

        Returns:
            str: Mapped status
        """
        if pd.isna(value) or value is None:
            return "Pendente"

        status = str(value).strip()
        if not status:
            return "Pendente"

        mapped_status = self.STATUS_MAPPING.get(status.lower())
        return mapped_status or "Pendente"

    def _parse_optional_date(self, value: Any) -> Optional[datetime]:
        """Parse optional date without time, returning midnight."""
        if pd.isna(value) or value is None:
            return None
        if isinstance(value, datetime):
            return value.replace(hour=0, minute=0, second=0, microsecond=0)
        if isinstance(value, str):
            for fmt in ["%d/%m/%Y", "%Y-%m-%d"]:
                try:
                    dt = datetime.strptime(value.strip(), fmt)
                    return dt
                except ValueError:
                    continue
        return None

    def _parse_optional_time(self, value: Any) -> Optional[str]:
        """Parse optional HH:MM time string."""
        if pd.isna(value) or value is None:
            return None
        if isinstance(value, str):
            import re

            m = re.match(r"^(\d{1,2}):(\d{2})", value.strip())
            if m:
                hours = int(m.group(1))
                minutes = int(m.group(2))
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    return f"{hours:02d}:{minutes:02d}"
        return None

    def _parse_confirmacao_datetime(
        self, data_hora_combined: Any, data_separada: Any, hora_separada: Any
    ) -> tuple[Optional[datetime], Optional[str]]:
        """
        Parse confirmation datetime from combined field or separate fields.

        Args:
            data_hora_combined: Combined date/time field value
            data_separada: Separate date field value
            hora_separada: Separate time field value

        Returns:
            tuple: (parsed_date, parsed_time) or (None, None)
        """
        # Primeiro tentar campos separados (mais confiáveis)
        if data_separada is not None and not pd.isna(data_separada):
            data_conf = self._parse_optional_date(data_separada)
            hora_conf = self._parse_optional_time(hora_separada)
            return data_conf, hora_conf

        # Tentar campo combinado
        if data_hora_combined is not None and not pd.isna(data_hora_combined):
            combined_str = str(data_hora_combined).strip()

            # Verificar se não é um valor inválido/placeholder
            if combined_str.lower() in ["whatss", "whats", "nan", ""]:
                return None, None

            # Tentar parsing como datetime completo
            try:
                if isinstance(data_hora_combined, datetime):
                    dt = data_hora_combined
                    data_conf = dt.replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    hora_conf = dt.strftime("%H:%M")
                    return data_conf, hora_conf

                # Tentar parsing de string com vários formatos
                for fmt in [
                    "%d/%m/%Y %H:%M",
                    "%d/%m/%Y %H:%M:%S",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                ]:
                    try:
                        dt = datetime.strptime(combined_str, fmt)
                        data_conf = dt.replace(
                            hour=0, minute=0, second=0, microsecond=0
                        )
                        hora_conf = dt.strftime("%H:%M")
                        return data_conf, hora_conf
                    except ValueError:
                        continue

            except Exception:
                pass

        return None, None

    async def _normalize_addresses_batch(
        self, appointments: List[Appointment]
    ) -> List[Appointment]:
        """
        Normalize addresses for a batch of appointments.

        Args:
            appointments: List of appointments to normalize

        Returns:
            List of appointments with normalized addresses
        """
        normalized_appointments = []

        for appointment in appointments:
            if (
                appointment.endereco_completo
                and not appointment.endereco_normalizado
            ):
                try:
                    normalized = await self.address_service.normalize_address(
                        appointment.endereco_completo
                    )
                    if normalized:
                        # Create a new appointment with normalized address
                        appointment_dict = appointment.model_dump()
                        appointment_dict["endereco_normalizado"] = normalized
                        normalized_appointments.append(
                            Appointment(**appointment_dict)
                        )
                    else:
                        normalized_appointments.append(appointment)
                except Exception as e:
                    # Log error but don't fail the whole batch
                    print(
                        f"Erro na normalização para '{appointment.endereco_completo}': {e}"
                    )
                    normalized_appointments.append(appointment)
            else:
                normalized_appointments.append(appointment)

        return normalized_appointments

    async def _normalize_documents_batch(
        self, appointments: List[Appointment]
    ) -> List[Appointment]:
        """
        Normalize documents for a batch of appointments.

        Args:
            appointments: List of appointments to normalize

        Returns:
            List of appointments with normalized documents
        """
        normalized_appointments = []

        for appointment in appointments:
            if (
                appointment.documento_completo
                and not appointment.documento_normalizado
            ):
                try:
                    normalized = (
                        await self.document_service.normalize_documents(
                            appointment.documento_completo
                        )
                    )
                    if normalized:
                        # Create a new appointment with normalized documents
                        appointment_dict = appointment.model_dump()
                        appointment_dict["documento_normalizado"] = normalized
                        appointment_dict["cpf"] = normalized.get("cpf")
                        appointment_dict["rg"] = normalized.get("rg")
                        normalized_appointments.append(
                            Appointment(**appointment_dict)
                        )
                    else:
                        normalized_appointments.append(appointment)
                except Exception as e:
                    # Log error but don't fail the whole batch
                    print(
                        f"Erro na normalização de documento para '{appointment.documento_completo}': {e}"
                    )
                    normalized_appointments.append(appointment)
            else:
                normalized_appointments.append(appointment)

        return normalized_appointments

    def _decide_status(self, row: pd.Series) -> str:
        """Decide final status based on explicit and confirmation fields."""
        status_confirmacao = self._clean_string(
            row.get("Status Confirmação")
            or row.get("Status Confirmacao")
            or row.get("Status de Confirmação")
        )

        if status_confirmacao and status_confirmacao.lower() == "confirmado":
            return "Confirmado"

        return "Pendente"

    def get_file_info(self, file_content: BinaryIO, filename: str) -> Dict:
        """
        Get basic information about the Excel file.

        Args:
            file_content: Binary content of the file
            filename: Name of the file

        Returns:
            Dict: File information
        """
        try:
            df = pd.read_excel(file_content)

            return {
                "filename": filename,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": list(df.columns),
                "has_required_columns": all(
                    col in df.columns
                    for col in [
                        "Nome da Marca",
                        "Nome da Unidade",
                        "Nome do Paciente",
                    ]
                ),
                "file_size": (
                    len(file_content.getvalue())  # type: ignore
                    if hasattr(file_content, "getvalue")
                    else 0
                ),
            }

        except Exception as e:
            return {"filename": filename, "error": str(e), "file_size": 0}

    async def _process_car(
        self, car_string: str, processed_cars: set
    ) -> Optional[str]:
        """
        Process car registration from appointment data.

        Args:
            car_string: Car string from appointment (e.g., "CENTER 3 CARRO 1 - UND84")
            processed_cars: Set of already processed car strings

        Returns:
            Optional[str]: Car ID if found or created, None if failed
        """
        if not self.car_service or not car_string:
            return None

        try:
            # Use the car service to find or create the car
            result = await self.car_service.find_or_create_car_from_string(
                car_string
            )

            if result.get("success"):
                car_data = result.get("car")
                if car_data:
                    return str(car_data.id)

            return None

        except Exception as e:
            # Log error but don't fail the entire import
            print(f"Erro ao processar carro '{car_string}': {e}")
            return None
