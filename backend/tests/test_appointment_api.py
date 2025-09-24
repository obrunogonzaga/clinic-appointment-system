"""API tests for appointment endpoints."""

from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.application.dtos.appointment_dto import (
    AppointmentFullUpdateDTO,
    AppointmentResponseDTO,
)
from src.domain.entities.user import User
from src.main import app
from src.presentation.api.v1.endpoints.appointments import (
    get_appointment_service,
)
from src.presentation.dependencies.auth import get_current_active_user


@pytest.fixture
def active_user() -> User:
    """Authenticated user injected into route dependencies."""

    return User(
        email="user@example.com",
        name="Usuário Teste",
        password_hash="hashed",
        is_admin=True,
        is_active=True,
    )


@pytest.fixture
def client(active_user: User) -> TestClient:
    """Create test client for API interactions."""

    async def override_current_user() -> User:
        return active_user

    app.dependency_overrides[get_current_active_user] = override_current_user

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)


def _build_response_dto() -> AppointmentResponseDTO:
    """Helper to create a response DTO with default values."""
    return AppointmentResponseDTO(
        id=uuid4(),
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Paciente",
        data_agendamento=datetime(2025, 1, 10, 9, 0),
        hora_agendamento="09:00",
        tipo_consulta=None,
        status="Confirmado",
        telefone="11999988888",
        carro=None,
        observacoes=None,
        driver_id=None,
        collector_id=None,
        cep=None,
        endereco_coleta=None,
        endereco_completo=None,
        endereco_normalizado=None,
        documento_completo=None,
        documento_normalizado=None,
        cpf=None,
        rg=None,
        numero_convenio=None,
        nome_convenio=None,
        carteira_convenio=None,
        created_at=datetime(2025, 1, 10, 9, 0),
        updated_at=None,
    )


def test_create_appointment_success(client: TestClient) -> None:
    """Endpoint should create appointment and return 201."""
    payload = {
        "nome_marca": "Marca",
        "nome_unidade": "Unidade",
        "nome_paciente": "Paciente",
        "data_agendamento": "2025-01-10T09:00:00",
        "hora_agendamento": "09:00",
        "status": "Confirmado",
        "telefone": "11999988888",
    }

    service_mock = MagicMock()
    service_mock.create_appointment = AsyncMock(
        return_value={
            "success": True,
            "message": "Agendamento criado com sucesso",
            "appointment": _build_response_dto(),
        }
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_appointment_service] = override_service
    try:
        response = client.post("/api/v1/appointments/", json=payload)
    finally:
        app.dependency_overrides.pop(get_appointment_service, None)

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["nome_paciente"] == "Paciente"
    assert data["message"] == "Agendamento criado com sucesso"


@pytest.mark.parametrize(
    "error_code,status_code",
    [
        ("duplicate", 409),
        ("validation", 400),
        ("internal", 500),
    ],
)
def test_create_appointment_error_responses(
    client: TestClient, error_code: str, status_code: int
) -> None:
    """Endpoint should map service error codes to HTTP status."""
    payload = {
        "nome_marca": "Marca",
        "nome_unidade": "Unidade",
        "nome_paciente": "Paciente",
        "data_agendamento": "2025-01-10T09:00:00",
        "hora_agendamento": "09:00",
        "status": "Confirmado",
        "telefone": "11999988888",
    }

    service_mock = MagicMock()
    service_mock.create_appointment = AsyncMock(
        return_value={
            "success": False,
            "message": "Erro",
            "error_code": error_code,
        }
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_appointment_service] = override_service
    try:
        response = client.post("/api/v1/appointments/", json=payload)
    finally:
        app.dependency_overrides.pop(get_appointment_service, None)

    assert response.status_code == status_code
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Erro"


def test_get_appointment_success(client: TestClient) -> None:
    """Endpoint should return appointment details when service succeeds."""

    appointment_id = str(uuid4())
    dto = _build_response_dto()
    dto.id = uuid4()

    service_mock = MagicMock()
    service_mock.get_appointment = AsyncMock(
        return_value={
            "success": True,
            "message": "Agendamento encontrado",
            "appointment": dto,
        }
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_appointment_service] = override_service
    try:
        response = client.get(f"/api/v1/appointments/{appointment_id}")
    finally:
        app.dependency_overrides.pop(get_appointment_service, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["nome_paciente"] == dto.nome_paciente
    service_mock.get_appointment.assert_awaited_once_with(appointment_id)


def test_get_appointment_not_found(client: TestClient) -> None:
    """Endpoint should propagate 404 when service reports missing appointment."""

    appointment_id = str(uuid4())
    service_mock = MagicMock()
    service_mock.get_appointment = AsyncMock(
        return_value={
            "success": False,
            "message": "Agendamento não encontrado",
            "error_code": "not_found",
        }
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_appointment_service] = override_service
    try:
        response = client.get(f"/api/v1/appointments/{appointment_id}")
    finally:
        app.dependency_overrides.pop(get_appointment_service, None)

    assert response.status_code == 404
    error = response.json()
    assert error["message"] == "Agendamento não encontrado"


def test_partial_update_appointment_success(client: TestClient) -> None:
    """PATCH endpoint should return updated appointment on success."""

    appointment_id = str(uuid4())
    dto = _build_response_dto()

    service_mock = MagicMock()
    service_mock.update_appointment = AsyncMock(
        return_value={
            "success": True,
            "message": "Agendamento atualizado com sucesso",
            "appointment": dto,
        }
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_appointment_service] = override_service
    try:
        response = client.patch(
            f"/api/v1/appointments/{appointment_id}",
            json={"nome_paciente": "Paciente Editado"},
        )
    finally:
        app.dependency_overrides.pop(get_appointment_service, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Agendamento atualizado com sucesso"
    service_mock.update_appointment.assert_awaited_once()


def test_partial_update_updates_confirmation_channel(client: TestClient) -> None:
    """PATCH endpoint should pass through confirmation channel changes."""

    appointment_id = str(uuid4())
    updated_dto = _build_response_dto()
    updated_dto.canal_confirmacao = "Telefone"

    service_mock = MagicMock()
    service_mock.update_appointment = AsyncMock(
        return_value={
            "success": True,
            "message": "Agendamento atualizado com sucesso",
            "appointment": updated_dto,
        }
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_appointment_service] = override_service
    try:
        response = client.patch(
            f"/api/v1/appointments/{appointment_id}",
            json={"canal_confirmacao": "Telefone"},
        )
    finally:
        app.dependency_overrides.pop(get_appointment_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["canal_confirmacao"] == "Telefone"
    service_mock.update_appointment.assert_awaited_once_with(
        appointment_id,
        AppointmentFullUpdateDTO(canal_confirmacao="Telefone"),
        updated_by="Usuário Teste",
    )


def test_partial_update_appointment_validation_error(client: TestClient) -> None:
    """PATCH endpoint should map validation errors to HTTP 400."""

    service_mock = MagicMock()
    service_mock.update_appointment = AsyncMock(
        return_value={
            "success": False,
            "message": "Dados inválidos",
            "error_code": "validation",
        }
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_appointment_service] = override_service
    try:
        response = client.patch(
            f"/api/v1/appointments/{uuid4()}",
            json={"status": ""},
        )
    finally:
        app.dependency_overrides.pop(get_appointment_service, None)

    assert response.status_code == 400
    error = response.json()
    assert error["message"] == "Dados inválidos"


def test_partial_update_appointment_not_found(client: TestClient) -> None:
    """PATCH endpoint should return 404 when service reports missing entity."""

    service_mock = MagicMock()
    service_mock.update_appointment = AsyncMock(
        return_value={
            "success": False,
            "message": "Agendamento não encontrado",
            "error_code": "not_found",
        }
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_appointment_service] = override_service
    try:
        response = client.patch(
            f"/api/v1/appointments/{uuid4()}",
            json={"nome_paciente": "Paciente"},
        )
    finally:
        app.dependency_overrides.pop(get_appointment_service, None)

    assert response.status_code == 404
    error = response.json()
    assert error["message"] == "Agendamento não encontrado"
