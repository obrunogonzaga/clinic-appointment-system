"""API tests for client management endpoints."""

from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.application.dtos.appointment_dto import PaginationDTO
from src.application.dtos.client_dto import (
    ClientAppointmentHistoryDTO,
    ClientDetailDTO,
    ClientSummaryDTO,
)
from src.domain.entities.user import User
from src.main import app
from src.presentation.api.v1.endpoints.clients import get_client_service
from src.presentation.dependencies.auth import (
    get_current_active_user,
    get_current_admin_user,
)


VALID_CPF = "52998224725"


@pytest.fixture
def active_user() -> User:
    return User(
        email="tester@example.com",
        name="Tester",
        password_hash="hashed",
        is_admin=True,
        is_active=True,
    )


@pytest.fixture
def client(active_user: User) -> TestClient:
    async def override_current_user() -> User:
        return active_user

    app.dependency_overrides[get_current_active_user] = override_current_user
    app.dependency_overrides[get_current_admin_user] = override_current_user

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_current_active_user, None)
        app.dependency_overrides.pop(get_current_admin_user, None)


def _build_summary() -> ClientSummaryDTO:
    return ClientSummaryDTO(
        id=uuid4(),
        nome_completo="Maria Cliente",
        cpf=VALID_CPF,
        cpf_formatado="529.982.247-25",
        telefone="11999999999",
        email="maria@example.com",
        total_agendamentos=1,
        ultima_data_agendamento=None,
        ultima_unidade=None,
        ultima_marca=None,
        ultima_consulta_tipo=None,
        ultima_consulta_status=None,
        created_at=datetime.utcnow(),
        updated_at=None,
    )


from datetime import datetime


def _build_detail() -> ClientDetailDTO:
    summary = _build_summary()
    history = [
        ClientAppointmentHistoryDTO(
            appointment_id=uuid4(),
            nome_marca="Marca",
            nome_unidade="Unidade",
            nome_paciente="Maria Cliente",
            data_agendamento=datetime(2025, 6, 1, 9, 0),
            hora_agendamento="09:00",
            status="Confirmado",
            tipo_consulta="Consulta",
            observacoes=None,
            created_at=datetime.utcnow(),
        )
    ]
    return ClientDetailDTO(**summary.model_dump(), appointment_history=history)


def test_list_clients_success(client: TestClient) -> None:
    service_mock = MagicMock()
    service_mock.list_clients = AsyncMock(
        return_value={
            "success": True,
            "clients": [_build_summary()],
            "pagination": PaginationDTO(
                page=1,
                page_size=20,
                total_items=1,
                total_pages=1,
                has_next=False,
                has_previous=False,
            ),
        }
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_client_service] = override_service
    try:
        response = client.get("/api/v1/clients")
    finally:
        app.dependency_overrides.pop(get_client_service, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["clients"]) == 1


def test_create_client_success(client: TestClient) -> None:
    service_mock = MagicMock()
    detail = _build_detail()
    service_mock.create_client = AsyncMock(
        return_value={"success": True, "message": "Cliente criado", "client": detail}
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_client_service] = override_service
    payload = {"nome_completo": "Maria Cliente", "cpf": VALID_CPF}
    try:
        response = client.post("/api/v1/clients", json=payload)
    finally:
        app.dependency_overrides.pop(get_client_service, None)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["client"]["nome_completo"] == "Maria Cliente"


@pytest.mark.parametrize(
    "error_code,status_code",
    [("duplicate", 409), ("validation", 400), ("internal", 500)],
)
def test_create_client_error_mapping(client: TestClient, error_code: str, status_code: int) -> None:
    service_mock = MagicMock()
    service_mock.create_client = AsyncMock(
        return_value={"success": False, "message": "Erro", "error_code": error_code}
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_client_service] = override_service
    try:
        response = client.post(
            "/api/v1/clients",
            json={"nome_completo": "Maria Cliente", "cpf": VALID_CPF},
        )
    finally:
        app.dependency_overrides.pop(get_client_service, None)

    assert response.status_code == status_code
    body = response.json()
    assert body["message"] == "Erro"


def test_get_client_not_found(client: TestClient) -> None:
    service_mock = MagicMock()
    service_mock.get_client = AsyncMock(
        return_value={"success": False, "message": "Cliente não encontrado", "error_code": "not_found"}
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_client_service] = override_service
    try:
        response = client.get(f"/api/v1/clients/{uuid4()}")
    finally:
        app.dependency_overrides.pop(get_client_service, None)

    assert response.status_code == 404
    assert response.json()["message"] == "Cliente não encontrado"


def test_update_client_success(client: TestClient) -> None:
    service_mock = MagicMock()
    detail = _build_detail()
    service_mock.update_client = AsyncMock(
        return_value={"success": True, "message": "Atualizado", "client": detail}
    )

    async def override_service() -> MagicMock:
        return service_mock

    app.dependency_overrides[get_client_service] = override_service
    client_id = str(uuid4())
    try:
        response = client.put(
            f"/api/v1/clients/{client_id}", json={"telefone": "11999999999"}
        )
    finally:
        app.dependency_overrides.pop(get_client_service, None)

    assert response.status_code == 200
    assert response.json()["success"] is True
