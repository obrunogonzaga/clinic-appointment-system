"""Tests for appointment service business logic."""

import io
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from types import SimpleNamespace

from src.application.dtos.appointment_dto import (
    AppointmentCreateDTO,
    AppointmentFullUpdateDTO,
)
from src.application.services.appointment_service import AppointmentService
from src.domain.entities.appointment import Appointment
from src.domain.entities.tag import Tag, TagReference
from src.domain.entities.logistics_package import LogisticsPackage


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
        cpf="52998224725",
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
        cpf="52998224725",
    )

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is False
    assert result["error_code"] == "duplicate"
    repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_dashboard_stats_applies_date_range() -> None:
    """Service should pass parsed datetime bounds to repository."""
    repository = MagicMock()
    stats_payload = {
        "total_appointments": 2,
        "confirmed_appointments": 1,
        "cancelled_appointments": 1,
        "total_units": 1,
        "total_brands": 1,
    }
    repository.get_appointment_stats = AsyncMock(return_value=stats_payload)

    service = AppointmentService(repository, excel_parser=MagicMock())

    result = await service.get_dashboard_stats(
        start_date="2025-09-25", end_date="2025-09-26"
    )

    assert result["success"] is True
    assert result["stats"] == stats_payload
    repository.get_appointment_stats.assert_awaited_once()
    called_start, called_end = repository.get_appointment_stats.await_args.args
    assert called_start == datetime(2025, 9, 25)
    assert called_end == datetime(2025, 9, 26)


@pytest.mark.asyncio
async def test_get_dashboard_stats_invalid_range() -> None:
    """Service should reject ranges where end is before or equal start."""
    repository = MagicMock()
    repository.get_appointment_stats = AsyncMock()

    service = AppointmentService(repository, excel_parser=MagicMock())

    result = await service.get_dashboard_stats(
        start_date="2025-01-10", end_date="2025-01-09"
    )

    assert result["success"] is False
    assert "end_date" in (result.get("message") or "")
    repository.get_appointment_stats.assert_not_called()


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
        cpf="52998224725",
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
        cpf="52998224725",
    )

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is False
    assert result["error_code"] == "internal"


@pytest.mark.asyncio
async def test_import_excel_blocks_past_dates() -> None:
    """Import should fail when appointments contain past-dated entries."""

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    past_day = today - timedelta(days=1)

    appointment = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=past_day,
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        cpf="52998224725",
    )

    parse_result = SimpleNamespace(
        success=True,
        appointments=[appointment],
        errors=[],
        total_rows=1,
        valid_rows=1,
        invalid_rows=0,
    )

    repository = MagicMock()
    repository.create_many = AsyncMock()
    excel_parser = MagicMock()
    excel_parser.parse_excel_file = AsyncMock(return_value=parse_result)

    service = AppointmentService(repository, excel_parser=excel_parser)

    result = await service.import_appointments_from_excel(
        io.BytesIO(b""),
        "agendamentos.xlsx",
        replace_existing=False,
        uploaded_by="Analista",
    )

    assert result["success"] is False
    assert result["past_appointments_blocked"] == 1
    assert result["imported_appointments"] == 0
    assert "passado" in result["message"].lower()
    assert any("anterior a hoje" in message.lower() for message in result["errors"])
    repository.create_many.assert_not_awaited()


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
        cpf="52998224725",
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
        cpf="52998224725",
    )

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is True
    assert result["appointment"].agendado_por == "Ana Admin"


@pytest.mark.asyncio
async def test_create_appointment_with_logistics_package() -> None:
    """Selecting a logistics package should override logistics fields automatically."""

    repository = MagicMock()
    repository.find_duplicates = AsyncMock(return_value=[])
    repository.create = AsyncMock(side_effect=lambda appointment: appointment)

    package = LogisticsPackage(
        nome="Combo Manhã",
        descricao="",
        driver_id="driver-1",
        driver_nome="João Motorista",
        collector_id="collector-1",
        collector_nome="Maria Coletora",
        car_id="car-1",
        car_nome="Kombi Azul",
        car_unidade="UND-01",
        car_display_name="Carro: Kombi Azul | Unidade: UND-01",
    )

    logistics_repo = MagicMock()
    logistics_repo.find_by_id = AsyncMock(return_value=package)

    service = AppointmentService(
        repository,
        excel_parser=MagicMock(),
        logistics_package_repository=logistics_repo,
    )

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        logistics_package_id=str(package.id),
        cpf="52998224725",
    )

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is True
    appointment = result["appointment"]
    assert appointment.driver_id == "driver-1"
    assert appointment.collector_id == "collector-1"
    assert appointment.car_id == "car-1"
    assert appointment.carro == "Carro: Kombi Azul | Unidade: UND-01"
    assert appointment.logistics_package_id == str(package.id)
    assert appointment.logistics_package_name == "Combo Manhã"
    logistics_repo.find_by_id.assert_awaited_once_with(str(package.id))


@pytest.mark.asyncio
async def test_create_appointment_invalid_logistics_package() -> None:
    """Service should surface error when selected package does not exist."""

    repository = MagicMock()
    repository.find_duplicates = AsyncMock(return_value=[])

    logistics_repo = MagicMock()
    logistics_repo.find_by_id = AsyncMock(return_value=None)

    service = AppointmentService(
        repository,
        excel_parser=MagicMock(),
        logistics_package_repository=logistics_repo,
    )

    dto = AppointmentCreateDTO(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        logistics_package_id="missing",
        cpf="52998224725",
    )

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is False
    assert result["error_code"] == "logistics_package_not_found"
    repository.create.assert_not_called()


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
        cpf="52998224725",
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
        cpf="52998224725",
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
        cpf="52998224725",
    )

    result = await service.create_appointment(dto, created_by="Ana Admin")

    assert result["success"] is False
    assert result["error_code"] == "limit_exceeded"
    tag_repo.find_by_ids.assert_not_called()


@pytest.mark.asyncio
async def test_get_appointment_success() -> None:
    """Service should return appointment when repository finds it."""

    appointment = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        cpf="52998224725",
    )

    repository = MagicMock()
    repository.find_by_id = AsyncMock(return_value=appointment)

    service = AppointmentService(repository, excel_parser=MagicMock())

    result = await service.get_appointment(str(appointment.id))

    assert result["success"] is True
    assert result["appointment"].id == appointment.id
    repository.find_by_id.assert_awaited_once_with(str(appointment.id))


@pytest.mark.asyncio
async def test_get_appointment_not_found() -> None:
    """Service should flag not_found when repository returns None."""

    repository = MagicMock()
    repository.find_by_id = AsyncMock(return_value=None)

    service = AppointmentService(repository, excel_parser=MagicMock())

    result = await service.get_appointment(str(uuid4()))

    assert result["success"] is False
    assert result["error_code"] == "not_found"


@pytest.mark.asyncio
async def test_update_appointment_success() -> None:
    """Service should merge updates, validate and persist before returning."""

    appointment = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        cpf="52998224725",
    )

    tag_id = uuid4()
    repository = MagicMock()
    repository.find_by_id = AsyncMock(return_value=appointment)

    updated_appointment = appointment.model_copy(deep=True)
    updated_appointment.status = "Agendado"
    updated_appointment.agendado_por = "Editor"
    updated_appointment.tags = [
        TagReference(id=str(tag_id), name="Urgente", color="#ff0000")
    ]
    repository.update = AsyncMock(return_value=updated_appointment)

    tag_repo = MagicMock()
    tag_repo.find_by_ids = AsyncMock(
        return_value=[Tag(id=tag_id, name="Urgente", color="#ff0000")]
    )

    service = AppointmentService(
        repository,
        excel_parser=MagicMock(),
        tag_repository=tag_repo,
        max_tags_per_appointment=5,
    )

    dto = AppointmentFullUpdateDTO(status="Agendado", tags=[str(tag_id)])
    result = await service.update_appointment(
        str(appointment.id), dto, updated_by="Editor"
    )

    assert result["success"] is True
    assert result["appointment"].status == "Agendado"
    assert result["appointment"].agendado_por == "Editor"
    repository.update.assert_awaited_once()
    call_args = repository.update.await_args
    assert call_args.args[0] == str(appointment.id)
    payload = call_args.args[1]
    assert payload["status"] == "Agendado"
    assert payload["agendado_por"] == "Editor"
    assert payload["tags"] == [
        {"id": str(tag_id), "name": "Urgente", "color": "#ff0000"}
    ]


@pytest.mark.asyncio
async def test_update_appointment_assigns_logistics_package() -> None:
    """Updating with a package ID should apply combo logistics info."""

    appointment = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        cpf="52998224725",
    )

    repository = MagicMock()
    repository.find_by_id = AsyncMock(return_value=appointment)

    package = LogisticsPackage(
        nome="Combo",
        descricao=None,
        driver_id="driver-1",
        driver_nome="João",
        collector_id="collector-1",
        collector_nome="Maria",
        car_id="car-1",
        car_nome="Kombi",
        car_unidade="UND-01",
        car_display_name="Carro: Kombi | Unidade: UND-01",
    )

    logistics_repo = MagicMock()
    logistics_repo.find_by_id = AsyncMock(return_value=package)

    updated = appointment.model_copy(update={
        "logistics_package_id": str(package.id),
        "logistics_package_name": package.nome,
        "driver_id": package.driver_id,
        "collector_id": package.collector_id,
        "car_id": package.car_id,
        "carro": package.car_display_name,
    })
    repository.update = AsyncMock(return_value=updated)

    service = AppointmentService(
        repository,
        excel_parser=MagicMock(),
        logistics_package_repository=logistics_repo,
    )

    dto = AppointmentFullUpdateDTO(logistics_package_id=str(package.id))
    result = await service.update_appointment("apt-id", dto)

    assert result["success"] is True
    logistics_repo.find_by_id.assert_awaited_once_with(str(package.id))
    updates = repository.update.await_args.args[1]
    assert updates["logistics_package_id"] == str(package.id)
    assert updates["driver_id"] == "driver-1"


@pytest.mark.asyncio
async def test_update_appointment_logistics_package_not_found() -> None:
    """Missing package should cancel update with descriptive error."""

    appointment = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        cpf="52998224725",
    )

    repository = MagicMock()
    repository.find_by_id = AsyncMock(return_value=appointment)

    logistics_repo = MagicMock()
    logistics_repo.find_by_id = AsyncMock(return_value=None)

    service = AppointmentService(
        repository,
        excel_parser=MagicMock(),
        logistics_package_repository=logistics_repo,
    )

    result = await service.update_appointment(
        "apt-id", AppointmentFullUpdateDTO(logistics_package_id="missing")
    )

    assert result["success"] is False
    assert result["error_code"] == "logistics_package_not_found"
    repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_appointment_clears_logistics_package() -> None:
    """Empty payload should remove stored package linkage."""

    appointment = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        logistics_package_id="pkg",
        logistics_package_name="Combo",
        driver_id="driver-1",
        collector_id="collector-1",
        car_id="car-1",
    )

    repository = MagicMock()
    repository.find_by_id = AsyncMock(return_value=appointment)
    repository.update = AsyncMock(
        return_value=appointment.model_copy(update={
            "logistics_package_id": None,
            "logistics_package_name": None,
        })
    )

    service = AppointmentService(repository, excel_parser=MagicMock())

    dto = AppointmentFullUpdateDTO(logistics_package_id="  ")
    result = await service.update_appointment("apt-id", dto)

    assert result["success"] is True
    updates = repository.update.await_args.args[1]
    assert updates["logistics_package_id"] is None
    assert updates["logistics_package_name"] is None


@pytest.mark.asyncio
async def test_update_appointment_invalid_tag() -> None:
    """Service should reject updates referencing nonexistent tags."""

    appointment = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
    )

    repository = MagicMock()
    repository.find_by_id = AsyncMock(return_value=appointment)

    tag_repo = MagicMock()
    tag_repo.find_by_ids = AsyncMock(return_value=[])

    service = AppointmentService(
        repository,
        excel_parser=MagicMock(),
        tag_repository=tag_repo,
    )

    dto = AppointmentFullUpdateDTO(tags=[str(uuid4())])
    result = await service.update_appointment(str(appointment.id), dto)

    assert result["success"] is False
    assert result["error_code"] == "invalid_tag"
    repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_appointment_validation_error() -> None:
    """Service should surface validation errors from domain model."""

    appointment = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
    )

    repository = MagicMock()
    repository.find_by_id = AsyncMock(return_value=appointment)

    service = AppointmentService(repository, excel_parser=MagicMock())

    dto = AppointmentFullUpdateDTO(telefone="123")
    result = await service.update_appointment(str(appointment.id), dto)

    assert result["success"] is False
    assert result["error_code"] == "validation"
    repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_appointment_updates_confirmation_channel() -> None:
    """Service should persist confirmation channel changes."""

    appointment = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999988888",
        canal_confirmacao="WhatsApp",
    )

    repository = MagicMock()
    repository.find_by_id = AsyncMock(return_value=appointment)

    updated = appointment.model_copy(update={"canal_confirmacao": "Telefone"})
    repository.update = AsyncMock(return_value=updated)

    service = AppointmentService(repository, excel_parser=MagicMock())

    dto = AppointmentFullUpdateDTO(canal_confirmacao="Telefone")
    result = await service.update_appointment(str(appointment.id), dto)

    assert result["success"] is True
    assert result["appointment"].canal_confirmacao == "Telefone"
    repository.update.assert_awaited_once()
    update_payload = repository.update.await_args.args[1]
    assert update_payload["canal_confirmacao"] == "Telefone"
