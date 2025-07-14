"""
Service for parsing Excel files containing appointment data.
"""

import io
from datetime import datetime
from typing import BinaryIO, Dict, List, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, ValidationError

from src.domain.entities.appointment import Appointment


class ExcelParseResult(BaseModel):
    """Result of Excel parsing operation."""
    
    success: bool
    appointments: List[Appointment] = []
    errors: List[str] = []
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    
    
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
        "Nomes dos Exames": "tipo_consulta"
    }
    
    # Status mapping from Excel to our domain model
    STATUS_MAPPING = {
        "Confirmado": "Confirmado",
        "Cancelado": "Cancelado", 
        "Reagendado": "Reagendado",
        "Realizado": "Concluído",
        "Não Compareceu": "Não Compareceu",
        "Agendado": "Confirmado",  # Default mapping
        "Efetivado": "Confirmado"
    }
    
    def __init__(self):
        """Initialize the parser service."""
        self.supported_formats = [".xlsx", ".xls", ".csv"]
    
    async def parse_excel_file(
        self,
        file_content: BinaryIO,
        filename: str
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
            df = await self._read_excel_file(file_content, filename)
            
            # Parse appointments
            return await self._parse_dataframe(df)
            
        except Exception as e:
            return ExcelParseResult(
                success=False,
                errors=[f"Erro ao ler arquivo Excel: {str(e)}"],
                total_rows=0
            )
    
    async def _read_excel_file(self, file_content: BinaryIO, filename: str) -> pd.DataFrame:
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
        if filename.endswith('.csv'):
            df = pd.read_csv(file_content, encoding='utf-8')
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_content, engine='openpyxl')
        elif filename.endswith('.xls'):
            # Try openpyxl first (for .xls files that are actually .xlsx)
            try:
                file_content.seek(0)
                df = pd.read_excel(file_content, engine='openpyxl')
            except Exception:
                # Fall back to xlrd for real .xls files
                file_content.seek(0)
                df = pd.read_excel(file_content, engine='xlrd')
        else:
            raise ValueError(f"Formato de arquivo não suportado: {filename}")
        
        # Basic validation
        if df.empty:
            raise ValueError("Arquivo Excel está vazio")
        
        # Check if required columns exist
        required_columns = ["Nome da Marca", "Nome da Unidade", "Nome do Paciente"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Colunas obrigatórias não encontradas: {', '.join(missing_columns)}")
        
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
        total_rows = len(df)
        
        for index, row in df.iterrows():
            try:
                appointment = await self._parse_row(row, index + 1)
                if appointment:
                    appointments.append(appointment)
                    
            except Exception as e:
                errors.append(f"Linha {index + 1}: {str(e)}")
        
        return ExcelParseResult(
            success=len(errors) == 0,
            appointments=appointments,
            errors=errors,
            total_rows=total_rows,
            valid_rows=len(appointments),
            invalid_rows=len(errors)
        )
    
    async def _parse_row(self, row: pd.Series, row_number: int) -> Optional[Appointment]:
        """
        Parse a single row into an Appointment entity.
        
        Args:
            row: Pandas Series representing a row
            row_number: Row number for error reporting
            
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
                raise ValueError("Campos obrigatórios em branco (Nome da Marca, Nome da Unidade, Nome do Paciente)")
            
            # Parse date and time
            data_agendamento, hora_agendamento = self._parse_datetime(
                row.get("Data/Hora Início Agendamento")
            )
            
            # Parse optional fields
            status = self._map_status(row.get("Status Agendamento"))
            telefone = self._clean_phone(row.get("Contato(s) do Paciente"))
            observacoes = self._clean_string(row.get("Observação"))
            tipo_consulta = self._clean_string(row.get("Nomes dos Exames"))
            
            # Create appointment entity
            appointment = Appointment(
                nome_marca=nome_marca,
                nome_unidade=nome_unidade,
                nome_paciente=nome_paciente,
                data_agendamento=data_agendamento,
                hora_agendamento=hora_agendamento,
                status=status,
                telefone=telefone,
                observacoes=observacoes,
                tipo_consulta=tipo_consulta
            )
            
            return appointment
            
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise ValueError(f"Erro de validação - {'; '.join(error_messages)}")
        except Exception as e:
            raise ValueError(f"Erro ao processar linha: {str(e)}")
    
    def _clean_string(self, value) -> Optional[str]:
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
    
    def _clean_phone(self, value) -> Optional[str]:
        """
        Clean and format phone number.
        
        Args:
            value: Raw phone value from Excel
            
        Returns:
            Optional[str]: Cleaned phone number or None
        """
        if pd.isna(value) or value is None:
            return None
        
        # Convert to string and clean
        phone_text = str(value).strip()
        
        # Extract phone numbers using regex
        import re
        
        # Look for "Celular: " pattern first
        celular_match = re.search(r'Celular:\s*([0-9\s\(\)\-]+)', phone_text)
        if celular_match:
            phone = celular_match.group(1)
        else:
            # Look for any phone-like pattern
            phone_match = re.search(r'([0-9\s\(\)\-]{8,})', phone_text)
            if phone_match:
                phone = phone_match.group(1)
            else:
                return None
        
        # Clean the extracted phone
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        phone = phone.replace("+55", "").replace("55", "", 1)  # Remove country code
        
        # Remove leading zeros if more than 11 digits
        if len(phone) > 11:
            phone = phone.lstrip('0')
        
        # Return phone if valid length
        return phone if 8 <= len(phone) <= 11 else None
    
    def _parse_datetime(self, value) -> Tuple[datetime, str]:
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
            for fmt in ["%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]:
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
        data_agendamento = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        hora_agendamento = dt.strftime("%H:%M")
        
        return data_agendamento, hora_agendamento
    
    def _map_status(self, value) -> str:
        """
        Map status from Excel to our domain model.
        
        Args:
            value: Raw status value from Excel
            
        Returns:
            str: Mapped status
        """
        if pd.isna(value) or value is None:
            return "Confirmado"  # Default status
        
        status = str(value).strip()
        return self.STATUS_MAPPING.get(status, "Confirmado")
    
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
                    col in df.columns for col in ["Nome da Marca", "Nome da Unidade", "Nome do Paciente"]
                ),
                "file_size": len(file_content.getvalue()) if hasattr(file_content, 'getvalue') else 0
            }
            
        except Exception as e:
            return {
                "filename": filename,
                "error": str(e),
                "file_size": 0
            }