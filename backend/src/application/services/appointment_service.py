"""
Service for managing appointments business logic.
"""

from datetime import datetime, timedelta
from typing import Any, BinaryIO, Dict, Optional

from src.application.services.excel_parser_service import ExcelParserService
from src.domain.repositories.appointment_repository_interface import (
    AppointmentRepositoryInterface,
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
    ):
        """
        Initialize the service with dependencies.

        Args:
            appointment_repository: Repository for appointment persistence
            excel_parser: Service for parsing Excel files
        """
        self.appointment_repository = appointment_repository
        self.excel_parser = excel_parser

    async def import_appointments_from_excel(
        self,
        file_content: BinaryIO,
        filename: str,
        replace_existing: bool = False,
    ) -> Dict:
        """
        Import appointments from Excel file.

        Args:
            file_content: Binary content of the Excel file
            filename: Name of the uploaded file
            replace_existing: Whether to replace existing appointments

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

            # Save appointments to database
            saved_appointments = []
            if parse_result.appointments:
                saved_appointments = (
                    await self.appointment_repository.create_many(
                        parse_result.appointments
                    )
                )

            return {
                "success": True,
                "message": f"Arquivo processado com sucesso. {len(saved_appointments)} agendamentos importados.",
                "total_rows": parse_result.total_rows,
                "valid_rows": parse_result.valid_rows,
                "invalid_rows": parse_result.invalid_rows,
                "imported_appointments": len(saved_appointments),
                "errors": parse_result.errors,
                "filename": filename,
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
            }

    async def get_appointments_with_filters(
        self,
        nome_unidade: Optional[str] = None,
        nome_marca: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        status: Optional[str] = None,
        driver_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict:
        """
        Get appointments with filters and pagination.

        Args:
            nome_unidade: Filter by unit name
            nome_marca: Filter by brand name
            data_inicio: Filter by start date (YYYY-MM-DD)
            data_fim: Filter by end date (YYYY-MM-DD)
            status: Filter by status
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dict: Filtered appointments with pagination info
        """
        try:
            # Calculate pagination
            skip = (page - 1) * page_size

            # Parse dates if provided
            parsed_dates = self._parse_filter_dates(data_inicio, data_fim)

            # Get appointments
            appointments = await self.appointment_repository.find_by_filters(
                nome_unidade=nome_unidade,
                nome_marca=nome_marca,
                data_inicio=parsed_dates[0],
                data_fim=parsed_dates[1],
                status=status,
                driver_id=driver_id,
                skip=skip,
                limit=page_size,
            )

            # Get total count for pagination
            filters = self._build_pagination_filters(
                nome_unidade, nome_marca, status, parsed_dates
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
                "Confirmado",
                "Cancelado",
                "Reagendado",
                "Concluído",
                "Não Compareceu",
            ]

            return {
                "success": True,
                "units": units,
                "brands": brands,
                "statuses": statuses,
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

    async def update_appointment_status(
        self, appointment_id: str, new_status: str
    ) -> Dict:
        """
        Update appointment status.

        Args:
            appointment_id: ID of the appointment
            new_status: New status value

        Returns:
            Dict: Update result
        """
        try:
            # Validate status
            valid_statuses = [
                "Confirmado",
                "Cancelado",
                "Reagendado",
                "Concluído",
                "Não Compareceu",
            ]
            if new_status not in valid_statuses:
                return {
                    "success": False,
                    "message": f"Status inválido. Valores permitidos: {', '.join(valid_statuses)}",
                }

            # Update appointment
            updated = await self.appointment_repository.update(
                appointment_id, {"status": new_status}
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

    def _parse_filter_dates(
        self, data_inicio: Optional[str], data_fim: Optional[str]
    ) -> tuple[Optional[datetime], Optional[datetime]]:
        """Parse filter dates (YYYY-MM-DD) and normalize to full-day range.

        - If only ``data_inicio`` is provided, returns [start_of_day, end_of_day].
        - If both are provided and equal, expands ``data_fim`` to end_of_day.
        - If both are provided and different, returns the two midnights as-is
          (inclusive range will be built downstream with $gte/$lte).
        """

        parsed_data_inicio: Optional[datetime] = None
        parsed_data_fim: Optional[datetime] = None

        if data_inicio:
            parsed_data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        if data_fim:
            parsed_data_fim = datetime.strptime(data_fim, "%Y-%m-%d")

        # Normalize to full day when appropriate
        if parsed_data_inicio and not parsed_data_fim:
            # single-day filter → end of day
            parsed_data_fim = parsed_data_inicio + timedelta(days=1)
        if (
            parsed_data_inicio
            and parsed_data_fim
            and parsed_data_inicio.date() == parsed_data_fim.date()
        ):
            # same day → set end to next midnight
            parsed_data_fim = parsed_data_inicio + timedelta(days=1)

        return parsed_data_inicio, parsed_data_fim

    def _build_pagination_filters(
        self,
        nome_unidade: Optional[str],
        nome_marca: Optional[str],
        status: Optional[str],
        parsed_dates: tuple[Optional[datetime], Optional[datetime]],
    ) -> Dict[str, Any]:
        """Build filters for pagination count."""
        filters: Dict[str, Any] = {}
        if nome_unidade:
            filters["nome_unidade"] = {"$regex": nome_unidade, "$options": "i"}
        if nome_marca:
            filters["nome_marca"] = {"$regex": nome_marca, "$options": "i"}
        if status:
            filters["status"] = status
        if parsed_dates[0] or parsed_dates[1]:
            date_filter: Dict[str, Any] = {}
            if parsed_dates[0]:
                date_filter["$gte"] = parsed_dates[0]
            if parsed_dates[1]:
                date_filter["$lte"] = parsed_dates[1]
            filters["data_agendamento"] = date_filter
        return filters
