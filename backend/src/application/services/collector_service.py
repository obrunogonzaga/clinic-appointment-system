"""
Service for managing collectors business logic.
"""

from typing import Any, Dict, Optional

from src.application.dtos.collector_dto import (
    ActiveCollectorDTO,
    CollectorCreateDTO,
    CollectorResponseDTO,
    CollectorUpdateDTO,
)
from src.domain.entities.collector import Collector
from src.domain.repositories.collector_repository_interface import (
    CollectorRepositoryInterface,
)


class CollectorService:
    """
    Service for collector business logic.

    This service orchestrates collector operations including
    registration, validation, and persistence.
    """

    def __init__(self, collector_repository: CollectorRepositoryInterface):
        """
        Initialize the service with dependencies.

        Args:
            collector_repository: Repository for collector persistence
        """
        self.collector_repository = collector_repository

    async def create_collector(
        self, collector_data: CollectorCreateDTO
    ) -> Dict:
        """
        Create a new collector.

        Args:
            collector_data: DTO with collector creation data

        Returns:
            Dict: Creation result
        """
        try:
            # Check if CPF already exists
            existing_collector = await self.collector_repository.find_by_cpf(
                collector_data.cpf
            )
            if existing_collector:
                return {
                    "success": False,
                    "message": "CPF já cadastrado no sistema",
                    "field": "cpf",
                }

            # Create collector entity
            collector = Collector(
                nome_completo=collector_data.nome_completo,
                cpf=collector_data.cpf,
                telefone=collector_data.telefone,
                email=collector_data.email,
                data_nascimento=collector_data.data_nascimento,
                endereco=collector_data.endereco,
                status=collector_data.status,
                carro=collector_data.carro,
                observacoes=collector_data.observacoes,
                registro_profissional=collector_data.registro_profissional,
                especializacao=collector_data.especializacao,
            )

            # Save to database
            created_collector = await self.collector_repository.create(
                collector
            )

            return {
                "success": True,
                "message": "Coletora cadastrada com sucesso",
                "collector": CollectorResponseDTO(
                    **created_collector.model_dump()
                ),
            }

        except ValueError as e:
            return {"success": False, "message": str(e), "field": "validation"}
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro interno ao cadastrar coletora: {str(e)}",
            }

    async def update_collector(
        self, collector_id: str, collector_data: CollectorUpdateDTO
    ) -> Dict:
        """
        Update an existing collector.

        Args:
            collector_id: ID of the collector to update
            collector_data: DTO with update data

        Returns:
            Dict: Update result
        """
        try:
            # Check if collector exists
            existing_collector = await self.collector_repository.find_by_id(
                collector_id
            )
            if not existing_collector:
                return {"success": False, "message": "Coletora não encontrada"}

            # Validate CPF uniqueness if being updated
            cpf_validation = await self._validate_cpf_uniqueness(
                collector_data.cpf, existing_collector.cpf, collector_id
            )
            if not cpf_validation["success"]:
                return cpf_validation

            # Build update data (only include non-None values)
            update_data = self._build_update_data(collector_data)
            if not update_data:
                return {
                    "success": False,
                    "message": "Nenhum campo para atualizar",
                }

            # Update collector
            updated_collector = await self.collector_repository.update(
                collector_id, update_data
            )

            if updated_collector:
                return {
                    "success": True,
                    "message": "Coletora atualizada com sucesso",
                    "collector": CollectorResponseDTO(
                        **updated_collector.model_dump()
                    ),
                }
            else:
                return {
                    "success": False,
                    "message": "Erro ao atualizar coletora",
                }

        except ValueError as e:
            return {"success": False, "message": str(e), "field": "validation"}
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro interno ao atualizar coletora: {str(e)}",
            }

    async def get_collector_by_id(self, collector_id: str) -> Dict:
        """
        Get a collector by ID.

        Args:
            collector_id: ID of the collector

        Returns:
            Dict: Collector data or error
        """
        try:
            collector = await self.collector_repository.find_by_id(
                collector_id
            )

            if not collector:
                return {"success": False, "message": "Coletora não encontrada"}

            return {
                "success": True,
                "collector": CollectorResponseDTO(**collector.model_dump()),
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar coletora: {str(e)}",
            }

    async def get_collectors_with_filters(
        self,
        nome_completo: Optional[str] = None,
        cpf: Optional[str] = None,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict:
        """
        Get collectors with filters and pagination.

        Args:
            nome_completo: Filter by collector name
            cpf: Filter by CPF
            telefone: Filter by phone
            email: Filter by email
            status: Filter by status
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dict: Filtered collectors with pagination info
        """
        try:
            # Calculate pagination
            skip = (page - 1) * page_size

            # Get collectors
            collectors = await self.collector_repository.find_by_filters(
                nome_completo=nome_completo,
                cpf=cpf,
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
            if cpf:
                filters["cpf"] = cpf
            if telefone:
                filters["telefone"] = telefone
            if email:
                filters["email"] = {"$regex": email, "$options": "i"}
            if status:
                filters["status"] = status

            total_count = await self.collector_repository.count(filters)

            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size

            return {
                "success": True,
                "collectors": [
                    CollectorResponseDTO(**collector.model_dump())
                    for collector in collectors
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
                "message": f"Erro ao buscar coletoras: {str(e)}",
                "collectors": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False,
                },
            }

    async def delete_collector(self, collector_id: str) -> Dict:
        """
        Delete a collector.

        Args:
            collector_id: ID of the collector to delete

        Returns:
            Dict: Delete result
        """
        try:
            # Check if collector exists
            collector = await self.collector_repository.find_by_id(
                collector_id
            )
            if not collector:
                return {"success": False, "message": "Coletora não encontrada"}

            # TODO: Check if collector is assigned to any appointments
            # This would require checking the appointment repository
            # For now, we'll just delete the collector

            # Delete collector
            deleted = await self.collector_repository.delete(collector_id)

            if deleted:
                return {
                    "success": True,
                    "message": "Coletora excluída com sucesso",
                }
            else:
                return {
                    "success": False,
                    "message": "Erro ao excluir coletora",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao excluir coletora: {str(e)}",
            }

    async def get_active_collectors(self) -> Dict:
        """
        Get all active collectors (for dropdowns).

        Returns:
            Dict: List of active collectors
        """
        try:
            collectors = (
                await self.collector_repository.get_active_collectors()
            )

            return {
                "success": True,
                "collectors": [
                    ActiveCollectorDTO(
                        id=collector.id,
                        nome_completo=collector.nome_completo,
                        cpf=collector.cpf,
                        telefone=collector.telefone,
                    )
                    for collector in collectors
                ],
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar coletoras ativas: {str(e)}",
                "collectors": [],
            }

    async def update_collector_status(
        self, collector_id: str, new_status: str
    ) -> Dict:
        """
        Update collector status.

        Args:
            collector_id: ID of the collector
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

            # Update collector
            updated = await self.collector_repository.update(
                collector_id, {"status": new_status}
            )

            if updated:
                return {
                    "success": True,
                    "message": "Status atualizado com sucesso",
                    "collector": CollectorResponseDTO(**updated.model_dump()),
                }
            else:
                return {"success": False, "message": "Coletora não encontrada"}

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao atualizar status: {str(e)}",
            }

    async def get_collector_stats(self) -> Dict:
        """
        Get collector statistics for dashboard.

        Returns:
            Dict: Collector statistics
        """
        try:
            stats = await self.collector_repository.get_collector_stats()

            return {"success": True, "stats": stats}

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar estatísticas: {str(e)}",
                "stats": {
                    "total_collectors": 0,
                    "active_collectors": 0,
                    "inactive_collectors": 0,
                    "suspended_collectors": 0,
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

    async def _validate_cpf_uniqueness(
        self, new_cpf: Optional[str], existing_cpf: str, collector_id: str
    ) -> Dict:
        """Validate CPF uniqueness during update."""
        if new_cpf and new_cpf != existing_cpf:
            cpf_exists = await self.collector_repository.exists_by_cpf(
                new_cpf, exclude_id=collector_id
            )
            if cpf_exists:
                return {
                    "success": False,
                    "message": "CPF já cadastrado no sistema",
                    "field": "cpf",
                }
        return {"success": True}

    def _build_update_data(self, collector_data: CollectorUpdateDTO) -> Dict:
        """Build update data dictionary from DTO."""
        update_data = {}
        for field, value in collector_data.model_dump().items():
            if value is not None:
                update_data[field] = value
        return update_data
