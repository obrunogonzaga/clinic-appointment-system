"""Service layer for logistics packages."""

from typing import Any, Dict, Optional

from src.application.dtos.logistics_package_dto import (
    LogisticsPackageCreateDTO,
    LogisticsPackageResponseDTO,
    LogisticsPackageUpdateDTO,
)
from src.domain.entities.logistics_package import LogisticsPackage
from src.domain.repositories.car_repository_interface import CarRepositoryInterface
from src.domain.repositories.collector_repository_interface import (
    CollectorRepositoryInterface,
)
from src.domain.repositories.driver_repository_interface import (
    DriverRepositoryInterface,
)
from src.domain.repositories.logistics_package_repository_interface import (
    LogisticsPackageRepositoryInterface,
)


class LogisticsPackageService:
    """Encapsula regras de negócio para pacotes logísticos."""

    def __init__(
        self,
        logistics_package_repository: LogisticsPackageRepositoryInterface,
        driver_repository: DriverRepositoryInterface,
        collector_repository: CollectorRepositoryInterface,
        car_repository: CarRepositoryInterface,
    ) -> None:
        self.logistics_package_repository = logistics_package_repository
        self.driver_repository = driver_repository
        self.collector_repository = collector_repository
        self.car_repository = car_repository

    async def list_packages(self, status: Optional[str] = None) -> Dict[str, Any]:
        packages = await self.logistics_package_repository.find_all(status=status)
        return {
            "success": True,
            "packages": [self._to_response(package) for package in packages],
        }

    async def list_active_packages(self) -> Dict[str, Any]:
        return await self.list_packages(status="Ativo")

    async def get_package(self, package_id: str) -> Dict[str, Any]:
        package = await self.logistics_package_repository.find_by_id(package_id)
        if not package:
            return {
                "success": False,
                "message": "Pacote logístico não encontrado.",
                "error_code": "not_found",
            }

        return {
            "success": True,
            "package": self._to_response(package),
        }

    async def create_package(
        self, package_data: LogisticsPackageCreateDTO
    ) -> Dict[str, Any]:
        validations = await self._validate_references(
            driver_id=package_data.driver_id,
            collector_id=package_data.collector_id,
            car_id=package_data.car_id,
        )
        if "error" in validations:
            return validations

        driver = validations["driver"]
        collector = validations["collector"]
        car = validations["car"]

        descricao = (
            package_data.descricao.strip()
            if package_data.descricao and package_data.descricao.strip()
            else None
        )

        package = LogisticsPackage(
            nome=package_data.nome,
            descricao=descricao,
            driver_id=str(driver.id),
            driver_nome=driver.nome_completo,
            collector_id=str(collector.id),
            collector_nome=collector.nome_completo,
            car_id=str(car.id),
            car_nome=car.nome,
            car_unidade=car.unidade,
            car_display_name=self._build_car_display_name(car.nome, car.unidade),
        )

        created = await self.logistics_package_repository.create(package)
        return {
            "success": True,
            "package": self._to_response(created),
        }

    async def update_package(
        self, package_id: str, update_data: LogisticsPackageUpdateDTO
    ) -> Dict[str, Any]:
        existing = await self.logistics_package_repository.find_by_id(package_id)
        if not existing:
            return {
                "success": False,
                "message": "Pacote logístico não encontrado.",
                "error_code": "not_found",
            }

        updates: Dict[str, Any] = {}

        if update_data.nome is not None:
            nome = update_data.nome.strip()
            if not nome:
                return {
                    "success": False,
                    "message": "Nome do pacote não pode ficar vazio.",
                    "error_code": "validation",
                }
            updates["nome"] = nome

        if update_data.descricao is not None:
            descricao = update_data.descricao.strip()
            updates["descricao"] = descricao or None

        references_changed = False

        if update_data.driver_id is not None:
            driver_id = update_data.driver_id.strip()
            if not driver_id:
                return {
                    "success": False,
                    "message": "Informe um motorista válido.",
                    "error_code": "validation",
                }
            driver = await self._fetch_active_driver(driver_id)
            if "error" in driver:
                return driver
            driver_entity = driver["driver"]
            updates["driver_id"] = str(driver_entity.id)
            updates["driver_nome"] = driver_entity.nome_completo
            references_changed = True

        if update_data.collector_id is not None:
            collector_id = update_data.collector_id.strip()
            if not collector_id:
                return {
                    "success": False,
                    "message": "Informe uma coletora válida.",
                    "error_code": "validation",
                }
            collector = await self._fetch_active_collector(collector_id)
            if "error" in collector:
                return collector
            collector_entity = collector["collector"]
            updates["collector_id"] = str(collector_entity.id)
            updates["collector_nome"] = collector_entity.nome_completo
            references_changed = True

        if update_data.car_id is not None:
            car_id = update_data.car_id.strip()
            if not car_id:
                return {
                    "success": False,
                    "message": "Informe um carro válido.",
                    "error_code": "validation",
                }
            car = await self._fetch_active_car(car_id)
            if "error" in car:
                return car
            car_entity = car["car"]
            updates["car_id"] = str(car_entity.id)
            updates["car_nome"] = car_entity.nome
            updates["car_unidade"] = car_entity.unidade
            updates["car_display_name"] = self._build_car_display_name(
                car_entity.nome, car_entity.unidade
            )
            references_changed = True

        if update_data.status is not None:
            status = update_data.status.strip().title()
            if status not in {"Ativo", "Inativo"}:
                return {
                    "success": False,
                    "message": "Status inválido para pacote logístico.",
                    "error_code": "validation",
                }
            updates["status"] = status

        if not updates and not references_changed:
            return {
                "success": True,
                "message": "Nenhuma alteração realizada.",
                "package": self._to_response(existing),
            }

        updated = await self.logistics_package_repository.update(
            package_id, updates
        )
        if not updated:
            return {
                "success": False,
                "message": "Falha ao atualizar pacote logístico.",
                "error_code": "update_failed",
            }

        return {
            "success": True,
            "message": "Pacote logístico atualizado com sucesso.",
            "package": self._to_response(updated),
        }

    async def delete_package(self, package_id: str) -> Dict[str, Any]:
        deleted = await self.logistics_package_repository.delete(package_id)
        if not deleted:
            return {
                "success": False,
                "message": "Pacote logístico não encontrado.",
                "error_code": "not_found",
            }

        return {
            "success": True,
            "message": "Pacote logístico removido com sucesso.",
        }

    async def _validate_references(
        self, driver_id: str, collector_id: str, car_id: str
    ) -> Dict[str, Any]:
        driver_result = await self._fetch_active_driver(driver_id)
        if "error" in driver_result:
            return driver_result

        collector_result = await self._fetch_active_collector(collector_id)
        if "error" in collector_result:
            return collector_result

        car_result = await self._fetch_active_car(car_id)
        if "error" in car_result:
            return car_result

        return {
            "driver": driver_result["driver"],
            "collector": collector_result["collector"],
            "car": car_result["car"],
        }

    async def _fetch_active_driver(self, driver_id: str) -> Dict[str, Any]:
        driver = await self.driver_repository.find_by_id(driver_id)
        if not driver:
            return {
                "error": {
                    "message": "Motorista informado não foi encontrado.",
                    "error_code": "driver_not_found",
                }
            }

        if (driver.status or "Ativo") != "Ativo":
            return {
                "error": {
                    "message": "Motorista selecionado está inativo.",
                    "error_code": "driver_inactive",
                }
            }

        return {"driver": driver}

    async def _fetch_active_collector(self, collector_id: str) -> Dict[str, Any]:
        collector = await self.collector_repository.find_by_id(collector_id)
        if not collector:
            return {
                "error": {
                    "message": "Coletora informada não foi encontrada.",
                    "error_code": "collector_not_found",
                }
            }

        if (collector.status or "Ativo") != "Ativo":
            return {
                "error": {
                    "message": "Coletora selecionada está inativa.",
                    "error_code": "collector_inactive",
                }
            }

        return {"collector": collector}

    async def _fetch_active_car(self, car_id: str) -> Dict[str, Any]:
        car = await self.car_repository.find_by_id(car_id)
        if not car:
            return {
                "error": {
                    "message": "Carro informado não foi encontrado.",
                    "error_code": "car_not_found",
                }
            }

        if (car.status or "Ativo") != "Ativo":
            return {
                "error": {
                    "message": "Carro selecionado está indisponível.",
                    "error_code": "car_inactive",
                }
            }

        return {"car": car}

    def _build_car_display_name(self, car_name: str, unidade: Optional[str]) -> str:
        base = car_name.strip()
        if unidade and unidade.strip():
            return f"Carro: {base} | Unidade: {unidade.strip()}"
        return f"Carro: {base}"

    def _to_response(
        self, package: LogisticsPackage
    ) -> LogisticsPackageResponseDTO:
        data = package.model_dump()
        data["id"] = str(package.id)
        return LogisticsPackageResponseDTO(**data)

