"""
Service for managing cars business logic.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.application.dtos.car_dto import (
    ActiveCarDTO,
    CarCreateDTO,
    CarFilterDTO,
    CarFromStringDTO,
    CarResponseDTO,
    CarUpdateDTO,
)
from src.domain.entities.car import Car
from src.domain.repositories.car_repository_interface import (
    CarRepositoryInterface,
)


class CarService:
    """
    Service for car business logic.

    This service orchestrates car operations including
    registration, validation, and persistence.
    """

    def __init__(self, car_repository: CarRepositoryInterface):
        """
        Initialize the service with dependencies.

        Args:
            car_repository: Repository for car persistence
        """
        self.car_repository = car_repository

    async def create_car(self, car_data: CarCreateDTO) -> Dict:
        """
        Create a new car.

        Args:
            car_data: DTO with car creation data

        Returns:
            Dict: Creation result
        """
        try:
            # Check if car name already exists
            existing_car = await self.car_repository.find_by_nome(
                car_data.nome
            )
            if existing_car:
                return {
                    "success": False,
                    "message": "Carro com este nome já cadastrado no sistema",
                    "field": "nome",
                }

            # Check if license plate already exists (if provided)
            if car_data.placa:
                existing_placa = await self.car_repository.find_by_placa(
                    car_data.placa
                )
                if existing_placa:
                    return {
                        "success": False,
                        "message": "Carro com esta placa já cadastrado no sistema",
                        "field": "placa",
                    }

            # Create car entity
            car = Car(
                nome=car_data.nome,
                unidade=car_data.unidade,
                placa=car_data.placa,
                modelo=car_data.modelo,
                cor=car_data.cor,
                status=car_data.status,
                observacoes=car_data.observacoes,
            )

            # Save to database
            created_car = await self.car_repository.create(car)

            return {
                "success": True,
                "message": "Carro cadastrado com sucesso",
                "car": CarResponseDTO(**created_car.model_dump()),
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao cadastrar carro: {str(e)}",
                "error": str(e),
            }

    async def get_car_by_id(self, car_id: str) -> Dict:
        """
        Get a car by its ID.

        Args:
            car_id: Car unique identifier

        Returns:
            Dict: Car data or error message
        """
        try:
            car = await self.car_repository.find_by_id(car_id)
            if not car:
                return {
                    "success": False,
                    "message": "Carro não encontrado",
                }

            return {
                "success": True,
                "car": CarResponseDTO(**car.model_dump()),
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar carro: {str(e)}",
                "error": str(e),
            }

    async def update_car(self, car_id: str, car_data: CarUpdateDTO) -> Dict:
        """
        Update a car.

        Args:
            car_id: Car ID to update
            car_data: DTO with updated car data

        Returns:
            Dict: Update result
        """
        try:
            # Check if car exists
            existing_car = await self.car_repository.find_by_id(car_id)
            if not existing_car:
                return {
                    "success": False,
                    "message": "Carro não encontrado",
                }

            # Check for nome conflicts
            if car_data.nome:
                nome_conflict = await self.car_repository.exists_by_nome(
                    car_data.nome, exclude_id=car_id
                )
                if nome_conflict:
                    return {
                        "success": False,
                        "message": "Já existe outro carro com este nome",
                        "field": "nome",
                    }

            # Check for placa conflicts
            if car_data.placa:
                placa_conflict = await self.car_repository.exists_by_placa(
                    car_data.placa, exclude_id=car_id
                )
                if placa_conflict:
                    return {
                        "success": False,
                        "message": "Já existe outro carro com esta placa",
                        "field": "placa",
                    }

            # Prepare update data (only non-None fields)
            update_data = {
                k: v for k, v in car_data.model_dump().items() 
                if v is not None
            }
            update_data["updated_at"] = datetime.utcnow()

            # Update car
            updated_car = await self.car_repository.update(car_id, update_data)

            return {
                "success": True,
                "message": "Carro atualizado com sucesso",
                "car": CarResponseDTO(**updated_car.model_dump()),
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao atualizar carro: {str(e)}",
                "error": str(e),
            }

    async def delete_car(self, car_id: str) -> Dict:
        """
        Delete a car.

        Args:
            car_id: Car ID to delete

        Returns:
            Dict: Deletion result
        """
        try:
            # Check if car exists
            existing_car = await self.car_repository.find_by_id(car_id)
            if not existing_car:
                return {
                    "success": False,
                    "message": "Carro não encontrado",
                }

            # TODO: Check if car is being used in appointments
            # For now, we'll allow deletion

            # Delete car
            deleted = await self.car_repository.delete(car_id)
            if not deleted:
                return {
                    "success": False,
                    "message": "Erro ao excluir carro",
                }

            return {
                "success": True,
                "message": "Carro excluído com sucesso",
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao excluir carro: {str(e)}",
                "error": str(e),
            }

    async def list_cars(self, filters: CarFilterDTO) -> Dict:
        """
        List cars with optional filters and pagination.

        Args:
            filters: Filter parameters

        Returns:
            Dict: List of cars with pagination info
        """
        try:
            # Calculate pagination
            skip = (filters.page - 1) * filters.page_size

            # Get cars
            cars = await self.car_repository.find_by_filters(
                nome=filters.nome,
                unidade=filters.unidade,
                placa=filters.placa,
                modelo=filters.modelo,
                status=filters.status,
                skip=skip,
                limit=filters.page_size,
            )

            # Get total count
            filter_dict = {
                k: v for k, v in filters.model_dump().items() 
                if v is not None and k not in ["page", "page_size"]
            }
            total_items = await self.car_repository.count(filter_dict)

            # Calculate pagination info
            total_pages = (total_items + filters.page_size - 1) // filters.page_size
            has_next = filters.page < total_pages
            has_previous = filters.page > 1

            return {
                "success": True,
                "cars": [CarResponseDTO(**car.model_dump()) for car in cars],
                "pagination": {
                    "page": filters.page,
                    "page_size": filters.page_size,
                    "total_items": total_items,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_previous": has_previous,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao listar carros: {str(e)}",
                "error": str(e),
                "cars": [],
                "pagination": {
                    "page": filters.page,
                    "page_size": filters.page_size,
                    "total_items": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False,
                },
            }

    async def get_active_cars(self) -> Dict:
        """
        Get all active cars for dropdowns.

        Returns:
            Dict: List of active cars
        """
        try:
            cars = await self.car_repository.get_active_cars()

            return {
                "success": True,
                "cars": [
                    ActiveCarDTO(**car.model_dump()) for car in cars
                ],
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar carros ativos: {str(e)}",
                "error": str(e),
                "cars": [],
            }

    async def get_filter_options(self) -> Dict:
        """
        Get filter options for dropdowns.

        Returns:
            Dict: Filter options
        """
        try:
            statuses = await self.car_repository.get_distinct_values("status")
            unidades = await self.car_repository.get_distinct_values("unidade")

            return {
                "success": True,
                "statuses": statuses,
                "unidades": unidades,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar opções de filtro: {str(e)}",
                "error": str(e),
                "statuses": [],
                "unidades": [],
            }

    async def get_car_stats(self) -> Dict:
        """
        Get car statistics for dashboard.

        Returns:
            Dict: Car statistics
        """
        try:
            stats = await self.car_repository.get_car_stats()

            return {
                "success": True,
                "stats": stats,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao buscar estatísticas: {str(e)}",
                "error": str(e),
                "stats": {},
            }

    async def find_or_create_car_from_string(self, car_string: str) -> Dict:
        """
        Find or create a car from appointment string format.
        
        This method is used during Excel import to automatically
        register cars that don't exist yet.

        Args:
            car_string: String like "CENTER 3 CARRO 1 - UND84"

        Returns:
            Dict: Car data and creation info
        """
        try:
            # Try to find existing car by exact name match
            existing_car = await self.car_repository.find_by_nome(car_string)
            if existing_car:
                return {
                    "success": True,
                    "car": CarResponseDTO(**existing_car.model_dump()),
                    "created": False,
                    "message": "Carro já existente"
                }

            # Extract car info from string
            try:
                car_name, unit = Car.extract_car_info_from_string(car_string)
            except ValueError:
                # If extraction fails, use the whole string as car name
                car_name = car_string.strip()
                unit = "UND"

            # Create new car
            car = Car(
                nome=car_name,
                unidade=unit,
                status="Ativo"
            )

            created_car = await self.car_repository.create(car)

            return {
                "success": True,
                "car": CarResponseDTO(**created_car.model_dump()),
                "created": True,
                "message": "Carro criado automaticamente"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao processar carro: {str(e)}",
                "error": str(e),
                "car": None,
                "created": False
            }