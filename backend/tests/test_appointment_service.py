"""Tests for appointment service business logic."""

from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.dtos.appointment_dto import AppointmentCreateDTO
from src.application.services.appointment_service import AppointmentService
from src.domain.entities.appointment import Appointment
from src.domain.entities.tag import Tag


@pytest.mark.asyncio
async def test_create_appointment_success() -> None:
    """Service should persist appointment when no duplicate exists."""
    repository = MagicMock()
    repository.find_duplicates = AsyncMock(return_value=[])
    repository.create = AsyncMock(side_effect=lambda appointment: appointment)

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

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is True
    assert result["appointment"].nome_paciente == "Paciente"
    assert result["appointment"].cadastrado_por == "Ana Admin"
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

    result = await service.create_appointment(dto, created_by="Ana Admin")

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

    result = await service.create_appointment(dto, created_by="Ana Admin")

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

    result = await service.create_appointment(dto, created_by="Ana Admin")

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

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is False
    assert result["error_code"] == "validation"
    repository.find_duplicates.assert_not_called()


@pytest.mark.asyncio
async def test_create_appointment_sets_agendado_por_when_status_agendado() -> None:
    """Agendado_por should capture creator when status starts as Agendado."""
    repository = MagicMock()
    repository.find_duplicates = AsyncMock(return_value=[])
    repository.create = AsyncMock(side_effect=lambda appointment: appointment)

    service = AppointmentService(repository, excel_parser=MagicMock())

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Agendado",
        telefone="11999988888",
    )

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is True
    assert result["appointment"].agendado_por == "Ana Admin"


@pytest.mark.asyncio
async def test_create_appointment_with_tags_success() -> None:
    """Service should embed tag summaries when tags are provided."""
    repository = MagicMock()
    repository.find_duplicates = AsyncMock(return_value=[])
    repository.create = AsyncMock(side_effect=lambda appointment: appointment)

    tag_uuid = uuid4()
    tag_id = str(tag_uuid)
    tag_repo = MagicMock()
    tag_repo.find_by_ids = AsyncMock(
        return_value=[Tag(id=tag_uuid, name="Urgente", color="#ff0000")]
    )

    service = AppointmentService(
        repository,
        excel_parser=MagicMock(),
        tag_repository=tag_repo,
        max_tags_per_appointment=5,
    )

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        tags=[tag_id],
    )

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is True
    assert len(result["appointment"].tags) == 1
    assert result["appointment"].tags[0].name == "Urgente"
    tag_repo.find_by_ids.assert_awaited_once_with([tag_id])


@pytest.mark.asyncio
async def test_create_appointment_with_invalid_tag() -> None:
    """Invalid tag ids should block appointment creation."""
    repository = MagicMock()
    repository.find_duplicates = AsyncMock(return_value=[])

    tag_repo = MagicMock()
    tag_repo.find_by_ids = AsyncMock(return_value=[])

    service = AppointmentService(
        repository,
        excel_parser=MagicMock(),
        tag_repository=tag_repo,
    )

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        tags=[str(uuid4())],
    )

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is False
    assert result["error_code"] == "invalid_tag"
    repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_appointment_exceeds_tag_limit() -> None:
    """Requests exceeding the configured tag limit should be rejected."""
    repository = MagicMock()
    repository.find_duplicates = AsyncMock(return_value=[])

    tag_repo = MagicMock()
    tag_repo.find_by_ids = AsyncMock()

    service = AppointmentService(
        repository,
        excel_parser=MagicMock(),
        tag_repository=tag_repo,
        max_tags_per_appointment=1,
    )

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        tags=[str(uuid4()), str(uuid4())],
    )

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is False
    assert result["error_code"] == "limit_exceeded"
    tag_repo.find_by_ids.assert_not_called()
