"""Tests for appointment service business logic."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.dtos.appointment_dto import AppointmentCreateDTO
from src.application.services.appointment_service import AppointmentService
from src.domain.entities.appointment import Appointment


@pytest.mark.asyncio
async def test_create_appointment_success() -> None:
    """Service should persist appointment when no duplicate exists."""
    repository = MagicMock()
    created_entity = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
    )
    repository.find_duplicates = AsyncMock(return_value=[])
    repository.create = AsyncMock(return_value=created_entity)

    service = AppointmentService(repository, excel_parser=MagicMock())

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
    )

    result = await service.create_appointment(dto)

    assert result["success"] is True
    assert result["appointment"].nome_paciente == "Paciente"
    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_appointment_duplicate() -> None:
    """Service should prevent duplicated appointments."""
    repository = MagicMock()
    repository.find_duplicates = AsyncMock(return_value=["existing-id"])
    repository.create = AsyncMock()

    service = AppointmentService(repository, excel_parser=MagicMock())

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
    )

    result = await service.create_appointment(dto)

    assert result["success"] is False
    assert result["error_code"] == "duplicate"
    repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_appointment_validation_error() -> None:
    """Invalid domain data should surface as validation error."""
    repository = MagicMock()
    repository.find_duplicates = AsyncMock()

    service = AppointmentService(repository, excel_parser=MagicMock())

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Status-Invalido",
        telefone="11999988888",
    )

    result = await service.create_appointment(dto)

    assert result["success"] is False
    assert result["error_code"] == "validation"
    repository.find_duplicates.assert_not_called()


@pytest.mark.asyncio
async def test_create_appointment_internal_error() -> None:
    """Unexpected errors should be captured as internal failures."""
    repository = MagicMock()
    repository.find_duplicates = AsyncMock(return_value=[])
    repository.create = AsyncMock(side_effect=RuntimeError("DB down"))

    service = AppointmentService(repository, excel_parser=MagicMock())

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
    )

    result = await service.create_appointment(dto)

    assert result["success"] is False
    assert result["error_code"] == "internal"


@pytest.mark.asyncio
async def test_create_appointment_missing_phone() -> None:
    """Missing phone should trigger validation error."""
    repository = MagicMock()
    repository.find_duplicates = AsyncMock()

    service = AppointmentService(repository, excel_parser=MagicMock())

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
    )

    result = await service.create_appointment(dto)

    assert result["success"] is False
    assert result["error_code"] == "validation"
    repository.find_duplicates.assert_not_called()
