"""
Service for managing drivers business logic.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.application.dtos.driver_dto import (
    ActiveDriverDTO,
    DriverCreateDTO,
    DriverFilterDTO,
    DriverResponseDTO,
    DriverUpdateDTO,
)
from src.domain.entities.driver import Driver
from src.domain.repositories.driver_repository_interface import (
    DriverRepositoryInterface,
)


class DriverService:
    """
    Service for driver business logic.

    This service orchestrates driver operations including
    registration, validation, and persistence.
    """

    def __init__(self, driver_repository: DriverRepositoryInterface):
        """
        Initialize the service with dependencies.

        Args:
            driver_repository: Repository for driver persistence
        """
        self.driver_repository = driver_repository

    async def create_driver(self, driver_data: DriverCreateDTO) -> Dict:
        """
        Create a new driver.

        Args:
            driver_data: DTO with driver creation data

        Returns:
            Dict: Creation result
        """
        try:
            # Check if CNH already exists
            existing_driver = await self.driver_repository.find_by_cnh(
                driver_data.cnh
            )
            if existing_driver:
                return {
                    "success": False,
                    "message": "CNH já cadastrada no sistema",
                    "field": "cnh",
                }

            # Create driver entity
            driver = Driver(
                nome_completo=driver_data.nome_completo,
                cnh=driver_data.cnh,
                telefone=driver_data.telefone,
                email=driver_data.email,
                data_nascimento=driver_data.data_nascimento,
                endereco=driver_data.endereco,
                status=driver_data.status,
                carro=driver_data.carro,
                observacoes=driver_data.observacoes,
            )

            # Save to database
            created_driver = await self.driver_repository.create(driver)

            return {
                "success": True,
                "message": "Motorista cadastrado com sucesso",
                "driver": DriverResponseDTO(**created_driver.model_dump()),
            }

        except ValueError as e:
            return {"success": False, "message": str(e), "field": "validation"}
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro interno ao cadastrar motorista: {str(e)}",
            }

    async def update_driver(
        self, driver_id: str, driver_data: DriverUpdateDTO
    ) -> Dict:
        """
        Update an existing driver.

        Args:
            driver_id: ID of the driver to update
            driver_data: DTO with update data

        Returns:
            Dict: Update result
        """
        try:
            # Check if driver exists
            existing_driver = await self.driver_repository.find_by_id(
                driver_id
            )
            if not existing_driver:
                return {
                    "success": False,
                    "message": "Motorista não encontrado",
                }

            # Validate CNH uniqueness if being updated
            cnh_validation = await self._validate_cnh_uniqueness(
                driver_data.cnh, existing_driver.cnh, driver_id
            )
            if not cnh_validation["success"]:
                return cnh_validation

            # Build update data (only include non-None values)
            update_data = self._build_update_data(driver_data)
            if not update_data:
                return {
                    "success": False,
                    "message": "Nenhum campo para atualizar",
                }

            # Update driver
            updated_driver = await self.driver_repository.update(
                driver_id, update_data
            )

            if updated_driver:
                return {
                    "success": True,
                    "message": "Motorista atualizado com sucesso",
                    "driver": DriverResponseDTO(**updated_driver.model_dump()),
                }
            else:
                return {
                    "success": False,
                    "message": "Erro ao atualizar motorista",
                }

        except ValueError as e:
            return {"success": False, "message": str(e), "field": "validation"}
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro interno ao atualizar motorista: {str(e)}",
            }

    async def get_driver_by_id(self, driver_id: str) -> Dict:
        """
        Get a driver by ID.

        Args:
            driver_id: ID of the driver

        Returns:
            Dict: Driver data or error
        """
        try:
            driver = await self.driver_repository.find_by_id(driver_id)

            if not driver:
                return {
                    "success": False,
                    "message": "Motorista não encontrado",
                }

            return {
                "success": True,
                "driver": DriverResponseDTO(**driver.model_dump()),
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar motorista: {str(e)}",
            }

    async def get_drivers_with_filters(
        self,
        nome_completo: Optional[str] = None,
        cnh: Optional[str] = None,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict:
        """
        Get drivers with filters and pagination.

        Args:
            nome_completo: Filter by driver name
            cnh: Filter by CNH
            telefone: Filter by phone
            email: Filter by email
            status: Filter by status
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dict: Filtered drivers with pagination info
        """
        try:
            # Calculate pagination
            skip = (page - 1) * page_size

            # Get drivers
            drivers = await self.driver_repository.find_by_filters(
                nome_completo=nome_completo,
                cnh=cnh,
                telefone=telefone,
                email=email,
                status=status,
                skip=skip,
                limit=page_size,
            )

            # Get total count for pagination
            filters: Dict[str, Any] = {}
            if nome_completo:
                filters["nome_completo"] = {
                    "$regex": nome_completo,
                    "$options": "i",
                }
            if cnh:
                filters["cnh"] = cnh
            if telefone:
                filters["telefone"] = telefone
            if email:
                filters["email"] = {"$regex": email, "$options": "i"}
            if status:
                filters["status"] = status

            total_count = await self.driver_repository.count(filters)

            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size

            return {
                "success": True,
                "drivers": [
                    DriverResponseDTO(**driver.model_dump())
                    for driver in drivers
                ],
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
                "message": f"Erro ao buscar motoristas: {str(e)}",
                "drivers": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False,
                },
            }

    async def delete_driver(self, driver_id: str) -> Dict:
        """
        Delete a driver.

        Args:
            driver_id: ID of the driver to delete

        Returns:
            Dict: Delete result
        """
        try:
            # Check if driver exists
            driver = await self.driver_repository.find_by_id(driver_id)
            if not driver:
                return {
                    "success": False,
                    "message": "Motorista não encontrado",
                }

            # TODO: Check if driver is assigned to any appointments
            # This would require checking the appointment repository
            # For now, we'll just delete the driver

            # Delete driver
            deleted = await self.driver_repository.delete(driver_id)

            if deleted:
                return {
                    "success": True,
                    "message": "Motorista excluído com sucesso",
                }
            else:
                return {
                    "success": False,
                    "message": "Erro ao excluir motorista",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao excluir motorista: {str(e)}",
            }

    async def get_active_drivers(self) -> Dict:
        """
        Get all active drivers (for dropdowns).

        Returns:
            Dict: List of active drivers
        """
        try:
            drivers = await self.driver_repository.get_active_drivers()

            return {
                "success": True,
                "drivers": [
                    ActiveDriverDTO(
                        id=driver.id,
                        nome_completo=driver.nome_completo,
                        cnh=driver.cnh,
                        telefone=driver.telefone,
                    )
                    for driver in drivers
                ],
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar motoristas ativos: {str(e)}",
                "drivers": [],
            }

    async def update_driver_status(
        self, driver_id: str, new_status: str
    ) -> Dict:
        """
        Update driver status.

        Args:
            driver_id: ID of the driver
            new_status: New status value

        Returns:
            Dict: Update result
        """
        try:
            # Validate status
            valid_statuses = ["Ativo", "Inativo", "Suspenso", "Férias"]
            if new_status not in valid_statuses:
                return {
                    "success": False,
                    "message": f"Status inválido. Valores permitidos: {', '.join(valid_statuses)}",
                }

            # Update driver
            updated = await self.driver_repository.update(
                driver_id, {"status": new_status}
            )

            if updated:
                return {
                    "success": True,
                    "message": "Status atualizado com sucesso",
                    "driver": DriverResponseDTO(**updated.model_dump()),
                }
            else:
                return {
                    "success": False,
                    "message": "Motorista não encontrado",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao atualizar status: {str(e)}",
            }

    async def get_driver_stats(self) -> Dict:
        """
        Get driver statistics for dashboard.

        Returns:
            Dict: Driver statistics
        """
        try:
            stats = await self.driver_repository.get_driver_stats()

            return {"success": True, "stats": stats}

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar estatísticas: {str(e)}",
                "stats": {
                    "total_drivers": 0,
                    "active_drivers": 0,
                    "inactive_drivers": 0,
                    "suspended_drivers": 0,
                },
            }

    async def get_filter_options(self) -> Dict:
        """
        Get available filter options for the UI.

        Returns:
            Dict: Available filter options
        """
        try:
            # Get available statuses
            statuses = ["Ativo", "Inativo", "Suspenso", "Férias"]

            return {"success": True, "statuses": statuses}

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar opções de filtro: {str(e)}",
                "statuses": [],
            }

    async def _validate_cnh_uniqueness(
        self, new_cnh: Optional[str], existing_cnh: str, driver_id: str
    ) -> Dict:
        """Validate CNH uniqueness during update."""
        if new_cnh and new_cnh != existing_cnh:
            cnh_exists = await self.driver_repository.exists_by_cnh(
                new_cnh, exclude_id=driver_id
            )
            if cnh_exists:
                return {
                    "success": False,
                    "message": "CNH já cadastrada no sistema",
                    "field": "cnh",
                }
        return {"success": True}

    def _build_update_data(self, driver_data: DriverUpdateDTO) -> Dict:
        """Build update data dictionary from DTO."""
        update_data = {}
        for field, value in driver_data.model_dump().items():
            if value is not None:
                update_data[field] = value
        return update_data
