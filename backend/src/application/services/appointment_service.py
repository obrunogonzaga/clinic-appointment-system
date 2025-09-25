"""
Service for managing appointments business logic.
"""

from datetime import datetime, timedelta
from typing import Any, BinaryIO, Dict, List, Optional, Tuple

from pydantic import ValidationError

from src.application.dtos.appointment_dto import (
    AppointmentCreateDTO,
    AppointmentFullUpdateDTO,
    AppointmentResponseDTO,
    AppointmentScope,
)
from src.application.services.excel_parser_service import ExcelParserService
from src.domain.entities.appointment import Appointment
from src.domain.entities.tag import TagReference
from src.domain.repositories.appointment_repository_interface import (
    AppointmentRepositoryInterface,
)
from src.domain.repositories.tag_repository_interface import (
    TagRepositoryInterface,
)
from src.domain.repositories.logistics_package_repository_interface import (
    LogisticsPackageRepositoryInterface,
)


class AppointmentService:
    """
    Service for appointment business logic.

    This service orchestrates appointment operations including
    Excel import, validation, and persistence.
    """

    def __init__(
        self,
        appointment_repository: AppointmentRepositoryInterface,
        excel_parser: ExcelParserService,
        logistics_package_repository: Optional[
            LogisticsPackageRepositoryInterface
        ] = None,
        tag_repository: Optional[TagRepositoryInterface] = None,
        max_tags_per_appointment: int = 5,
    ):
        """
        Initialize the service with dependencies.

        Args:
            appointment_repository: Repository for appointment persistence
            excel_parser: Service for parsing Excel files
        """
        self.appointment_repository = appointment_repository
        self.excel_parser = excel_parser
        self.logistics_package_repository = logistics_package_repository
        self.tag_repository = tag_repository
        self.max_tags_per_appointment = max(max_tags_per_appointment, 0)

    async def _load_logistics_package(
        self, package_id: str
    ) -> Dict[str, Any]:
        if not package_id:
            return {"error": {"message": "ID do pacote não informado."}}

        if not self.logistics_package_repository:
            return {
                "error": {
                    "message": "Funcionalidade de pacotes logísticos não está configurada.",
                    "error_code": "logistics_package_unavailable",
                }
            }

        package = await self.logistics_package_repository.find_by_id(package_id)
        if not package:
            return {
                "error": {
                    "message": "Pacote logístico informado não foi encontrado.",
                    "error_code": "logistics_package_not_found",
                }
            }

        if package.status != "Ativo":
            return {
                "error": {
                    "message": "Pacote logístico informado está inativo.",
                    "error_code": "logistics_package_inactive",
                }
            }

        return {"package": package}

    async def import_appointments_from_excel(
        self,
        file_content: BinaryIO,
        filename: str,
        replace_existing: bool = False,
        uploaded_by: Optional[str] = None,
    ) -> Dict:
        """
        Import appointments from Excel file.

        Args:
            file_content: Binary content of the Excel file
            filename: Name of the uploaded file
            replace_existing: Whether to replace existing appointments
            uploaded_by: Name of the authenticated user performing the upload

        Returns:
            Dict: Import result with statistics
        """
        try:
            # Parse Excel file
            parse_result = await self.excel_parser.parse_excel_file(
                file_content, filename
            )

            if not parse_result.success:
                return {
                    "success": False,
                    "message": "Erro ao processar arquivo Excel",
                    "errors": parse_result.errors,
                    "total_rows": parse_result.total_rows,
                    "valid_rows": 0,
                    "invalid_rows": parse_result.invalid_rows,
                    "imported_appointments": 0,
                    "duplicates_found": 0,
                }

            uploader_name = uploaded_by.strip() if uploaded_by else None

            # Propagate metadata about the uploader before any persistence logic
            if uploader_name and parse_result.appointments:
                for appointment in parse_result.appointments:
                    appointment.cadastrado_por = uploader_name
                    if appointment.status == "Agendado":
                        appointment.agendado_por = uploader_name

            # Enforce temporal rules: appointments dated before today are rejected
            today_cutoff = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            blocked_by_past_dates = [
                appointment
                for appointment in parse_result.appointments
                if appointment.data_agendamento
                and appointment.data_agendamento < today_cutoff
            ]

            if blocked_by_past_dates:
                formatted_examples = [
                    f"{apt.nome_paciente} – {apt.data_agendamento.strftime('%d/%m/%Y')}"
                    for apt in blocked_by_past_dates[:5]
                ]

                errors = list(parse_result.errors)
                errors.insert(
                    0,
                    (
                        f"{len(blocked_by_past_dates)} agendamentos com data anterior a hoje "
                        "foram encontrados na planilha."
                    ),
                )

                return {
                    "success": False,
                    "message": "Planilha contém agendamentos com data no passado.",
                    "errors": errors,
                    "total_rows": parse_result.total_rows,
                    "valid_rows": max(
                        parse_result.valid_rows - len(blocked_by_past_dates), 0
                    ),
                    "invalid_rows": parse_result.invalid_rows
                    + len(blocked_by_past_dates),
                    "imported_appointments": 0,
                    "duplicates_found": 0,
                    "past_appointments_blocked": len(blocked_by_past_dates),
                    "past_appointments_examples": formatted_examples,
                }

            # Handle existing appointments if needed
            if replace_existing:
                # Get distinct units and brands from import
                units = list(
                    set(apt.nome_unidade for apt in parse_result.appointments)
                )
                brands = list(
                    set(apt.nome_marca for apt in parse_result.appointments)
                )

                # Delete existing appointments from same units/brands
                for unit in units:
                    for brand in brands:
                        await self.appointment_repository.delete_many(
                            {"nome_unidade": unit, "nome_marca": brand}
                        )

            # Check for duplicates before saving
            duplicates_found = 0
            saved_appointments = []

            if parse_result.appointments:
                # Find duplicate appointment IDs
                duplicate_ids = (
                    await self.appointment_repository.find_duplicates(
                        parse_result.appointments
                    )
                )
                duplicates_found = len(duplicate_ids)

                # Filter out duplicates to get only new appointments
                new_appointments = [
                    apt
                    for apt in parse_result.appointments
                    if str(apt.id) not in duplicate_ids
                ]

                # Save only the new appointments
                if new_appointments:
                    saved_appointments = (
                        await self.appointment_repository.create_many(
                            new_appointments
                        )
                    )

            # Build success message based on duplicates found
            if duplicates_found > 0:
                message = f"{len(saved_appointments)} agendamentos importados, {duplicates_found} duplicados ignorados."
            else:
                message = f"Arquivo processado com sucesso. {len(saved_appointments)} agendamentos importados."

            return {
                "success": True,
                "message": message,
                "total_rows": parse_result.total_rows,
                "valid_rows": parse_result.valid_rows,
                "invalid_rows": parse_result.invalid_rows,
                "imported_appointments": len(saved_appointments),
                "duplicates_found": duplicates_found,
                "errors": parse_result.errors,
                "filename": filename,
                "past_appointments_blocked": 0,
                "past_appointments_examples": [],
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro interno ao processar arquivo: {str(e)}",
                "errors": [str(e)],
                "total_rows": 0,
                "valid_rows": 0,
                "invalid_rows": 0,
                "imported_appointments": 0,
                "duplicates_found": 0,
            }

    async def get_appointments_with_filters(
        self,
        nome_unidade: Optional[str] = None,
        nome_marca: Optional[str] = None,
        data: Optional[str] = None,
        status: Optional[str] = None,
        driver_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        scope: AppointmentScope = AppointmentScope.CURRENT,
    ) -> Dict:
        """
        Get appointments with filters and pagination.

        Args:
            nome_unidade: Filter by unit name
            nome_marca: Filter by brand name
            data: Filter by specific date (YYYY-MM-DD)
            status: Filter by status
            driver_id: Filter by driver ID
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dict: Filtered appointments with pagination info
        """
        try:
            # Calculate pagination
            skip = (page - 1) * page_size

            # Parse date if provided
            parsed_dates = self._parse_filter_date(data)
            scope_bounds = self._resolve_scope_bounds(scope)
            date_bounds = self._merge_scope_with_dates(parsed_dates, scope_bounds)

            # Get appointments
            appointments = await self.appointment_repository.find_by_filters(
                nome_unidade=nome_unidade,
                nome_marca=nome_marca,
                data_inicio=date_bounds[0],
                data_fim=date_bounds[1],
                status=status,
                driver_id=driver_id,
                skip=skip,
                limit=page_size,
            )

            # Get total count for pagination
            filters = self._build_pagination_filters(
                nome_unidade, nome_marca, status, date_bounds
            )
            if driver_id:
                filters["driver_id"] = driver_id
            total_count = await self.appointment_repository.count(filters)

            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size

            return {
                "success": True,
                "appointments": [apt.model_dump() for apt in appointments],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_previous": page > 1,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar agendamentos: {str(e)}",
                "appointments": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False,
                },
            }

    async def create_appointment(
        self,
        appointment_data: AppointmentCreateDTO,
        created_by: Optional[str] = None,
    ) -> Dict:
        """Create a single appointment entry with metadata."""

        try:
            phone = (appointment_data.telefone or "").strip()
            if not phone:
                return {
                    "success": False,
                    "message": "Telefone é obrigatório para novo agendamento.",
                    "error_code": "validation",
                }
            cip_value = (
                appointment_data.cip.strip()
                if appointment_data.cip and appointment_data.cip.strip()
                else None
            )
            creator_name = created_by.strip() if created_by else None
            agendado_por = (
                creator_name
                if appointment_data.status == "Agendado" and creator_name
                else None
            )

            provided_tag_ids = list(dict.fromkeys(appointment_data.tags or []))
            tag_references: List[TagReference] = []
            if provided_tag_ids:
                if not self.tag_repository:
                    return {
                        "success": False,
                        "message": "Funcionalidade de tags não está configurada.",
                        "error_code": "unavailable",
                    }

                if (
                    self.max_tags_per_appointment
                    and len(provided_tag_ids) > self.max_tags_per_appointment
                ):
                    return {
                        "success": False,
                        "message": "Número máximo de tags por agendamento excedido.",
                        "error_code": "limit_exceeded",
                    }

                stored_tags = await self.tag_repository.find_by_ids(
                    provided_tag_ids
                )
                active_tags_map = {
                    str(tag.id): tag for tag in stored_tags if tag.is_active
                }
                missing_or_inactive = [
                    tag_id
                    for tag_id in provided_tag_ids
                    if tag_id not in active_tags_map
                ]
                if missing_or_inactive:
                    return {
                        "success": False,
                        "message": "Uma ou mais tags informadas são inválidas ou inativas.",
                        "error_code": "invalid_tag",
                        "invalid_tags": missing_or_inactive,
                    }

                tag_references = [
                    TagReference(
                        id=tag_id,
                        name=active_tags_map[tag_id].name,
                        color=active_tags_map[tag_id].color,
                    )
                    for tag_id in provided_tag_ids
                ]

            carro_value = (
                appointment_data.carro.strip()
                if appointment_data.carro and appointment_data.carro.strip()
                else None
            )
            car_id_value = (
                appointment_data.car_id.strip()
                if appointment_data.car_id and appointment_data.car_id.strip()
                else None
            )
            driver_id_value = (
                appointment_data.driver_id.strip()
                if appointment_data.driver_id and appointment_data.driver_id.strip()
                else None
            )
            collector_id_value = (
                appointment_data.collector_id.strip()
                if appointment_data.collector_id
                and appointment_data.collector_id.strip()
                else None
            )
            logistics_package_id = (
                appointment_data.logistics_package_id.strip()
                if appointment_data.logistics_package_id
                and appointment_data.logistics_package_id.strip()
                else None
            )
            logistics_package_name = None

            if logistics_package_id:
                package_result = await self._load_logistics_package(
                    logistics_package_id
                )
                if "error" in package_result:
                    error = package_result["error"]
                    return {
                        "success": False,
                        "message": error.get(
                            "message", "Pacote logístico inválido."
                        ),
                        "error_code": error.get(
                            "error_code", "invalid_logistics_package"
                        ),
                    }

                package = package_result["package"]
                logistics_package_id = str(package.id)
                logistics_package_name = package.nome
                driver_id_value = package.driver_id
                collector_id_value = package.collector_id
                car_id_value = package.car_id
                carro_value = package.car_display_name

            appointment = Appointment(
                nome_marca=appointment_data.nome_marca,
                nome_unidade=appointment_data.nome_unidade,
                nome_paciente=appointment_data.nome_paciente,
                data_agendamento=appointment_data.data_agendamento,
                hora_agendamento=appointment_data.hora_agendamento,
                tipo_consulta=appointment_data.tipo_consulta,
                cip=cip_value,
                status=appointment_data.status,
                telefone=phone,
                carro=carro_value,
                logistics_package_id=logistics_package_id,
                logistics_package_name=logistics_package_name,
                observacoes=appointment_data.observacoes,
                driver_id=driver_id_value,
                collector_id=collector_id_value,
                car_id=car_id_value,
                numero_convenio=appointment_data.numero_convenio,
                nome_convenio=appointment_data.nome_convenio,
                carteira_convenio=appointment_data.carteira_convenio,
                cadastrado_por=creator_name,
                agendado_por=agendado_por,
                tags=tag_references,
            )

            duplicate_ids = await self.appointment_repository.find_duplicates(
                [appointment]
            )
            if duplicate_ids:
                return {
                    "success": False,
                    "message": "Já existe um agendamento para este paciente nesta data e horário.",
                    "error_code": "duplicate",
                }

            created = await self.appointment_repository.create(appointment)

            return {
                "success": True,
                "message": "Agendamento criado com sucesso",
                "appointment": AppointmentResponseDTO(
                    **created.model_dump()
                ),
            }

        except ValueError as exc:
            return {
                "success": False,
                "message": str(exc),
                "error_code": "validation",
            }
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "success": False,
                "message": f"Erro ao criar agendamento: {str(exc)}",
                "error_code": "internal",
            }

    async def get_appointment(self, appointment_id: str) -> Dict:
        """Retrieve a single appointment by its identifier."""
        try:
            appointment = await self.appointment_repository.find_by_id(
                appointment_id
            )
            if not appointment:
                return {
                    "success": False,
                    "message": "Agendamento não encontrado",
                    "error_code": "not_found",
                }

            return {
                "success": True,
                "message": "Agendamento encontrado",
                "appointment": AppointmentResponseDTO(
                    **appointment.model_dump()
                ),
            }

        except Exception as exc:  # pragma: no cover - defensive
            return {
                "success": False,
                "message": f"Erro ao buscar agendamento: {str(exc)}",
                "error_code": "internal",
            }

    async def get_filter_options(self) -> Dict:
        """
        Get available filter options for the UI.

        Returns:
            Dict: Available filter options
        """
        try:
            # Get distinct values for filters
            units = await self.appointment_repository.get_distinct_values(
                "nome_unidade"
            )
            brands = await self.appointment_repository.get_distinct_values(
                "nome_marca"
            )

            # Get available statuses
            statuses = [
                "Pendente",
                "Autorização",
                "Cadastrar",
                "Agendado",
                "Confirmado",
                "Coletado",
                "Alterar",
                "Cancelado",
                "Recoleta",
            ]

            return {
                "success": True,
                "units": units,
                "brands": brands,
                "statuses": statuses,
                "max_tags_per_appointment": self.max_tags_per_appointment,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar opções de filtro: {str(e)}",
                "units": [],
                "brands": [],
                "statuses": [],
            }

    async def get_dashboard_stats(self) -> Dict:
        """
        Get dashboard statistics.

        Returns:
            Dict: Dashboard statistics
        """
        try:
            stats = await self.appointment_repository.get_appointment_stats()

            return {"success": True, "stats": stats}

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar estatísticas: {str(e)}",
                "stats": {
                    "total_appointments": 0,
                    "confirmed_appointments": 0,
                    "cancelled_appointments": 0,
                    "total_units": 0,
                    "total_brands": 0,
                },
            }

    async def delete_appointment(self, appointment_id: str) -> Dict:
        """
        Delete an appointment.

        Args:
            appointment_id: ID of the appointment to delete

        Returns:
            Dict: Delete result
        """
        try:
            # Check if appointment exists
            appointment = await self.appointment_repository.find_by_id(
                appointment_id
            )
            if not appointment:
                return {
                    "success": False,
                    "message": "Agendamento não encontrado",
                }

            # Delete appointment
            deleted = await self.appointment_repository.delete(appointment_id)

            if deleted:
                return {
                    "success": True,
                    "message": "Agendamento excluído com sucesso",
                }
            else:
                return {
                    "success": False,
                    "message": "Erro ao excluir agendamento",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao excluir agendamento: {str(e)}",
            }

    async def update_appointment(
        self,
        appointment_id: str,
        update_data: AppointmentFullUpdateDTO,
        updated_by: Optional[str] = None,
    ) -> Dict:
        """Update appointment core details (including tags)."""

        try:
            appointment = await self.appointment_repository.find_by_id(
                appointment_id
            )
            if not appointment:
                return {
                    "success": False,
                    "message": "Agendamento não encontrado",
                    "error_code": "not_found",
                }

            payload = update_data.model_dump(exclude_unset=True)
            if not payload:
                return {
                    "success": True,
                    "message": "Nenhuma alteração realizada",
                    "appointment": AppointmentResponseDTO(
                        **appointment.model_dump()
                    ),
                }

            sanitized_updates: Dict[str, Any] = {}
            tag_references_for_validation: Optional[List[TagReference]] = None

            if "logistics_package_id" in payload:
                raw_package_id = payload.pop("logistics_package_id")
                normalized_package_id = (
                    raw_package_id.strip()
                    if isinstance(raw_package_id, str)
                    and raw_package_id.strip()
                    else None
                )

                if normalized_package_id:
                    package_result = await self._load_logistics_package(
                        normalized_package_id
                    )
                    if "error" in package_result:
                        error = package_result["error"]
                        return {
                            "success": False,
                            "message": error.get(
                                "message", "Pacote logístico inválido."
                            ),
                            "error_code": error.get(
                                "error_code", "invalid_logistics_package"
                            ),
                        }

                    package = package_result["package"]
                    sanitized_updates["logistics_package_id"] = str(package.id)
                    sanitized_updates["logistics_package_name"] = package.nome
                    sanitized_updates["driver_id"] = package.driver_id
                    sanitized_updates["collector_id"] = package.collector_id
                    sanitized_updates["car_id"] = package.car_id
                    sanitized_updates["carro"] = package.car_display_name

                    payload.pop("driver_id", None)
                    payload.pop("collector_id", None)
                    payload.pop("car_id", None)
                    payload.pop("carro", None)
                else:
                    sanitized_updates["logistics_package_id"] = None
                    sanitized_updates["logistics_package_name"] = None

            for field, value in payload.items():
                if field in {
                    "nome_marca",
                    "nome_unidade",
                    "nome_paciente",
                    "tipo_consulta",
                    "status",
                    "carro",
                    "observacoes",
                    "numero_convenio",
                    "nome_convenio",
                    "carteira_convenio",
                    "cip",
                    "canal_confirmacao",
                }:
                    if value is None:
                        sanitized_updates[field] = None
                        continue
                    if isinstance(value, str):
                        trimmed = value.strip()
                        sanitized_updates[field] = trimmed or None
                    else:
                        sanitized_updates[field] = value
                    continue

                if field in {"driver_id", "collector_id", "car_id"}:
                    if value is None:
                        sanitized_updates[field] = None
                    elif isinstance(value, str):
                        sanitized_updates[field] = value.strip() or None
                    else:
                        sanitized_updates[field] = value
                    continue

                if field == "telefone":
                    if value is None:
                        sanitized_updates[field] = None
                    elif isinstance(value, str):
                        digits = "".join(ch for ch in value if ch.isdigit())
                        sanitized_updates[field] = digits or None
                    else:
                        sanitized_updates[field] = value
                    continue

                if field == "hora_agendamento":
                    if value is None:
                        sanitized_updates[field] = None
                    elif isinstance(value, str):
                        sanitized_updates[field] = value.strip()
                    else:
                        sanitized_updates[field] = value
                    continue

                if field == "tags":
                    provided_tag_ids = list(dict.fromkeys(value or []))
                    if provided_tag_ids and not self.tag_repository:
                        return {
                            "success": False,
                            "message": "Funcionalidade de tags não está configurada.",
                            "error_code": "unavailable",
                        }

                    if (
                        self.max_tags_per_appointment
                        and len(provided_tag_ids) > self.max_tags_per_appointment
                    ):
                        return {
                            "success": False,
                            "message": "Número máximo de tags por agendamento excedido.",
                            "error_code": "limit_exceeded",
                        }

                    tag_references: List[TagReference] = []
                    if provided_tag_ids and self.tag_repository:
                        stored_tags = await self.tag_repository.find_by_ids(
                            provided_tag_ids
                        )
                        active_tags_map = {
                            str(tag.id): tag for tag in stored_tags if tag.is_active
                        }
                        missing_or_inactive = [
                            tag_id
                            for tag_id in provided_tag_ids
                            if tag_id not in active_tags_map
                        ]
                        if missing_or_inactive:
                            return {
                                "success": False,
                                "message": "Uma ou mais tags informadas são inválidas ou inativas.",
                                "error_code": "invalid_tag",
                                "invalid_tags": missing_or_inactive,
                            }

                        tag_references = [
                            TagReference(
                                id=tag_id,
                                name=active_tags_map[tag_id].name,
                                color=active_tags_map[tag_id].color,
                            )
                            for tag_id in provided_tag_ids
                        ]

                    sanitized_updates[field] = [
                        tag.model_dump() for tag in tag_references
                    ]
                    tag_references_for_validation = tag_references
                    continue

                # Default assignment (includes datetime fields)
                sanitized_updates[field] = value

            validation_updates: Dict[str, Any] = dict(sanitized_updates)
            if tag_references_for_validation is not None:
                validation_updates["tags"] = tag_references_for_validation

            current_serialized = appointment.model_dump()
            base_data = {**current_serialized, **validation_updates}

            try:
                validated = Appointment(**base_data)
            except (ValidationError, ValueError) as exc:
                return {
                    "success": False,
                    "message": str(exc),
                    "error_code": "validation",
                }

            normalized = validated.model_dump()
            changes: Dict[str, Any] = {}
            for field in sanitized_updates:
                new_value = normalized.get(field)
                old_value = current_serialized.get(field)
                if field == "tags":
                    new_value = new_value or []
                    old_value = old_value or []
                if new_value != old_value:
                    changes[field] = new_value

            if "status" in changes and changes["status"] == "Agendado" and updated_by:
                changes["agendado_por"] = updated_by.strip()

            if not changes:
                return {
                    "success": True,
                    "message": "Nenhuma alteração realizada",
                    "appointment": AppointmentResponseDTO(**normalized),
                }

            updated = await self.appointment_repository.update(
                appointment_id, changes
            )

            if not updated:
                return {
                    "success": False,
                    "message": "Erro ao atualizar agendamento",
                    "error_code": "update_failed",
                }

            return {
                "success": True,
                "message": "Agendamento atualizado com sucesso",
                "appointment": AppointmentResponseDTO(
                    **updated.model_dump()
                ),
            }

        except Exception as exc:  # pragma: no cover - defensive
            return {
                "success": False,
                "message": f"Erro ao atualizar agendamento: {str(exc)}",
                "error_code": "internal",
            }

    async def update_appointment_status(
        self,
        appointment_id: str,
        new_status: str,
        updated_by: Optional[str] = None,
    ) -> Dict:
        """
        Update appointment status.

        Args:
            appointment_id: ID of the appointment
            new_status: New status value
            updated_by: Name of the user performing the status change

        Returns:
            Dict: Update result
        """
        try:
            # Validate status
            valid_statuses = [
                "Pendente",
                "Autorização",
                "Cadastrar",
                "Agendado",
                "Confirmado",
                "Coletado",
                "Alterar",
                "Cancelado",
                "Recoleta",
            ]
            if new_status not in valid_statuses:
                return {
                    "success": False,
                    "message": f"Status inválido. Valores permitidos: {', '.join(valid_statuses)}",
                }

            update_payload = {"status": new_status}
            if new_status == "Agendado" and updated_by:
                update_payload["agendado_por"] = updated_by.strip()

            updated = await self.appointment_repository.update(
                appointment_id, update_payload
            )

            if updated:
                return {
                    "success": True,
                    "message": "Status atualizado com sucesso",
                    "appointment": updated.model_dump(),
                }
            else:
                return {
                    "success": False,
                    "message": "Agendamento não encontrado",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao atualizar status: {str(e)}",
            }

    async def update_appointment_driver(
        self, appointment_id: str, driver_id: Optional[str]
    ) -> Dict:
        """
        Update appointment driver.

        Args:
            appointment_id: ID of the appointment
            driver_id: ID of the driver (can be None to remove driver)

        Returns:
            Dict: Update result
        """
        try:
            # Check if appointment exists
            appointment = await self.appointment_repository.find_by_id(
                appointment_id
            )
            if not appointment:
                return {
                    "success": False,
                    "message": "Agendamento não encontrado",
                }

            # Update appointment
            updated = await self.appointment_repository.update(
                appointment_id, {"driver_id": driver_id}
            )

            if updated:
                return {
                    "success": True,
                    "message": "Motorista atualizado com sucesso",
                    "appointment": updated.model_dump(),
                }
            else:
                return {
                    "success": False,
                    "message": "Erro ao atualizar motorista",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao atualizar motorista: {str(e)}",
            }

    async def update_appointment_collector(
        self, appointment_id: str, collector_id: Optional[str]
    ) -> Dict:
        """
        Update appointment collector.

        Args:
            appointment_id: ID of the appointment
            collector_id: ID of the collector (can be None to remove collector)

        Returns:
            Dict: Update result
        """
        try:
            # Check if appointment exists
            appointment = await self.appointment_repository.find_by_id(
                appointment_id
            )
            if not appointment:
                return {
                    "success": False,
                    "message": "Agendamento não encontrado",
                }

            # Update appointment
            updated = await self.appointment_repository.update(
                appointment_id, {"collector_id": collector_id}
            )

            if updated:
                return {
                    "success": True,
                    "message": "Coletora atualizada com sucesso",
                    "appointment": updated.model_dump(),
                }
            else:
                return {
                    "success": False,
                    "message": "Erro ao atualizar coletora",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao atualizar coletora: {str(e)}",
            }

    def _parse_filter_date(
        self, data: Optional[str]
    ) -> tuple[Optional[datetime], Optional[datetime]]:
        """Parse filter date and normalize to a full-day range.

        Accepts common formats used in the UI:
        - "YYYY-MM-DD" (HTML date input/ISO)
        - "DD/MM/YYYY" (pt-BR locale)

        Returns a tuple of (start_of_day, start_of_next_day) so that
        repository queries can use "$gte" for the start and "$lt" for the end.
        """

        if not data:
            return None, None

        value = data.strip()

        parsed_date: Optional[datetime] = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                parsed_date = datetime.strptime(value, fmt)
                break
            except ValueError:
                continue

        if parsed_date is None:
            # Re-raise with a clearer message so the API returns a helpful error
            raise ValueError(
                "Formato de data inválido. Use YYYY-MM-DD ou DD/MM/YYYY"
            )

        start_of_day = parsed_date
        end_of_day = parsed_date + timedelta(days=1)

        return start_of_day, end_of_day

    def _resolve_scope_bounds(
        self,
        scope: AppointmentScope,
        reference: Optional[datetime] = None,
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Return lower/upper bounds based on the requested scope."""

        current_reference = reference or datetime.utcnow()
        start_of_today = current_reference.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        if scope == AppointmentScope.CURRENT:
            return start_of_today, None
        if scope == AppointmentScope.HISTORY:
            return None, start_of_today
        return None, None

    def _merge_scope_with_dates(
        self,
        parsed_dates: Tuple[Optional[datetime], Optional[datetime]],
        scope_bounds: Tuple[Optional[datetime], Optional[datetime]],
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Combine explicit date filters with scope boundaries."""

        lower_candidates = [parsed_dates[0], scope_bounds[0]]
        lower_values = [value for value in lower_candidates if value is not None]
        merged_lower = max(lower_values) if lower_values else None

        upper_candidates = [parsed_dates[1], scope_bounds[1]]
        upper_values = [value for value in upper_candidates if value is not None]
        merged_upper = min(upper_values) if upper_values else None

        return merged_lower, merged_upper

    def _build_pagination_filters(
        self,
        nome_unidade: Optional[str],
        nome_marca: Optional[str],
        status: Optional[str],
        date_bounds: Tuple[Optional[datetime], Optional[datetime]],
    ) -> Dict[str, Any]:
        """Build filters for pagination count."""
        filters: Dict[str, Any] = {}
        if nome_unidade:
            filters["nome_unidade"] = {"$regex": nome_unidade, "$options": "i"}
        if nome_marca:
            filters["nome_marca"] = {"$regex": nome_marca, "$options": "i"}
        if status:
            filters["status"] = status
        if date_bounds[0] or date_bounds[1]:
            # Use "$lt" for the upper bound to match the repository behavior
            # (start inclusive, end exclusive).
            date_filter: Dict[str, Any] = {}
            if date_bounds[0]:
                date_filter["$gte"] = date_bounds[0]
            if date_bounds[1]:
                date_filter["$lt"] = date_bounds[1]
            filters["data_agendamento"] = date_filter
        return filters
