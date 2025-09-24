"""Unit tests for logistics package service."""

from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

from src.application.dtos.logistics_package_dto import (
    LogisticsPackageCreateDTO,
    LogisticsPackageUpdateDTO,
)
from src.application.services.logistics_package_service import (
    LogisticsPackageService,
)
from src.domain.entities.logistics_package import LogisticsPackage


def _build_service() -> LogisticsPackageService:
    """Create service with async repository stubs."""

    logistics_repo = AsyncMock()
    driver_repo = AsyncMock()
    collector_repo = AsyncMock()
    car_repo = AsyncMock()

    service = LogisticsPackageService(
        logistics_package_repository=logistics_repo,
        driver_repository=driver_repo,
        collector_repository=collector_repo,
        car_repository=car_repo,
    )

    return service


def _active_driver() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(), nome_completo="João Motorista", status="Ativo"
    )


def _active_collector() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(), nome_completo="Maria Coletora", status="Ativo"
    )


def _active_car() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(), nome="Kombi Azul", unidade="UND-01", status="Ativo"
    )


def _package_from_refs(
    driver: SimpleNamespace,
    collector: SimpleNamespace,
    car: SimpleNamespace,
) -> LogisticsPackage:
    return LogisticsPackage(
        nome="Combo Manhã",
        descricao=None,
        driver_id=str(driver.id),
        driver_nome=driver.nome_completo,
        collector_id=str(collector.id),
        collector_nome=collector.nome_completo,
        car_id=str(car.id),
        car_nome=car.nome,
        car_unidade=car.unidade,
        car_display_name=f"Carro: {car.nome} | Unidade: {car.unidade}",
    )


@pytest.mark.asyncio
async def test_list_packages_returns_serialized_objects() -> None:
    service = _build_service()
    driver = _active_driver()
    collector = _active_collector()
    car = _active_car()
    package = _package_from_refs(driver, collector, car)
    service.logistics_package_repository.find_all.return_value = [package]

    result = await service.list_packages()

    assert result["success"] is True
    assert len(result["packages"]) == 1
    service.logistics_package_repository.find_all.assert_awaited_once_with(
        status=None
    )


@pytest.mark.asyncio
async def test_list_active_packages_filters_by_status() -> None:
    service = _build_service()
    service.logistics_package_repository.find_all.return_value = []

    await service.list_active_packages()

    service.logistics_package_repository.find_all.assert_awaited_once_with(
        status="Ativo"
    )


@pytest.mark.asyncio
async def test_get_package_not_found() -> None:
    service = _build_service()
    service.logistics_package_repository.find_by_id.return_value = None

    result = await service.get_package("missing-id")

    assert result["success"] is False
    assert result["error_code"] == "not_found"


@pytest.mark.asyncio
async def test_create_package_success() -> None:
    service = _build_service()
    driver = _active_driver()
    collector = _active_collector()
    car = _active_car()

    service.driver_repository.find_by_id.return_value = driver
    service.collector_repository.find_by_id.return_value = collector
    service.car_repository.find_by_id.return_value = car

    created_package = _package_from_refs(driver, collector, car)
    service.logistics_package_repository.create.return_value = created_package

    dto = LogisticsPackageCreateDTO(
        nome="Combo Manhã",
        descricao="",
        driver_id=str(driver.id),
        collector_id=str(collector.id),
        car_id=str(car.id),
    )

    result = await service.create_package(dto)

    assert result["success"] is True
    service.logistics_package_repository.create.assert_awaited_once()
    payload = service.logistics_package_repository.create.await_args.args[0]
    assert payload.driver_nome == "João Motorista"
    assert payload.car_display_name.endswith("UND-01")


@pytest.mark.asyncio
async def test_create_package_driver_missing() -> None:
    service = _build_service()
    service.driver_repository.find_by_id.return_value = None

    dto = LogisticsPackageCreateDTO(
        nome="Combo Manhã",
        descricao=None,
        driver_id="unknown",
        collector_id="collector",
        car_id="car",
    )

    result = await service.create_package(dto)

    assert "error" in result
    assert result["error"]["error_code"] == "driver_not_found"


@pytest.mark.asyncio
async def test_update_package_no_changes_returns_original() -> None:
    service = _build_service()
    driver = _active_driver()
    collector = _active_collector()
    car = _active_car()
    existing = _package_from_refs(driver, collector, car)
    service.logistics_package_repository.find_by_id.return_value = existing

    result = await service.update_package("package-id", LogisticsPackageUpdateDTO())

    assert result["success"] is True
    assert result["message"] == "Nenhuma alteração realizada."
    service.logistics_package_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_package_rejects_invalid_status() -> None:
    service = _build_service()
    driver = _active_driver()
    collector = _active_collector()
    car = _active_car()
    existing = _package_from_refs(driver, collector, car)
    service.logistics_package_repository.find_by_id.return_value = existing

    result = await service.update_package(
        "package-id", LogisticsPackageUpdateDTO(status="Pausado")
    )

    assert result["success"] is False
    assert result["error_code"] == "validation"
    service.logistics_package_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_package_updates_references() -> None:
    service = _build_service()
    original_driver = _active_driver()
    collector = _active_collector()
    car = _active_car()
    existing = _package_from_refs(original_driver, collector, car)
    service.logistics_package_repository.find_by_id.return_value = existing

    new_driver = SimpleNamespace(
        id=uuid4(), nome_completo="Carlos Motorista", status="Ativo"
    )
    service.driver_repository.find_by_id.return_value = new_driver
    updated_entity = existing.model_copy(update={
        "driver_id": str(new_driver.id),
        "driver_nome": new_driver.nome_completo,
    })
    service.logistics_package_repository.update.return_value = updated_entity

    result = await service.update_package(
        "package-id", LogisticsPackageUpdateDTO(driver_id=str(new_driver.id))
    )

    assert result["success"] is True
    service.logistics_package_repository.update.assert_awaited_once()
    updates = service.logistics_package_repository.update.await_args.args[1]
    assert updates["driver_id"] == str(new_driver.id)
    assert updates["driver_nome"] == "Carlos Motorista"


@pytest.mark.asyncio
async def test_update_package_returns_driver_lookup_error() -> None:
    service = _build_service()
    driver = _active_driver()
    collector = _active_collector()
    car = _active_car()
    existing = _package_from_refs(driver, collector, car)
    service.logistics_package_repository.find_by_id.return_value = existing
    service.driver_repository.find_by_id.return_value = None

    result = await service.update_package(
        "package-id", LogisticsPackageUpdateDTO(driver_id="unknown")
    )

    assert "error" in result
    assert result["error"]["error_code"] == "driver_not_found"


@pytest.mark.asyncio
async def test_delete_package_success() -> None:
    service = _build_service()
    service.logistics_package_repository.delete.return_value = True

    result = await service.delete_package("package-id")

    assert result["success"] is True
    service.logistics_package_repository.delete.assert_awaited_once_with(
        "package-id"
    )


@pytest.mark.asyncio
async def test_delete_package_not_found() -> None:
    service = _build_service()
    service.logistics_package_repository.delete.return_value = False

    result = await service.delete_package("missing")

    assert result["success"] is False
    assert result["error_code"] == "not_found"


def test_build_car_display_name_without_unit() -> None:
    service = _build_service()

    label = service._build_car_display_name("Kombi Azul", unidade=None)

    assert label == "Carro: Kombi Azul"
