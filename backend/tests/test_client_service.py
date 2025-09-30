"""Tests for the client service covering manual and automatic flows."""

from datetime import datetime
from typing import Dict, List, Optional

import pytest

from src.application.dtos.client_dto import ClientCreateDTO, ClientUpdateDTO
from src.application.services.client_service import ClientService
from src.domain.entities.appointment import Appointment
from src.domain.entities.client import Client
from src.domain.repositories.client_repository_interface import ClientRepositoryInterface


VALID_CPF = "52998224725"
SECOND_VALID_CPF = "48449253691"


class InMemoryClientRepository(ClientRepositoryInterface):
    """Simple in-memory repository used for unit tests."""

    def __init__(self) -> None:
        self.storage: Dict[str, Client] = {}

    async def create(self, client: Client) -> Client:
        self.storage[str(client.id)] = client
        return client

    async def update(self, client: Client) -> Client:
        self.storage[str(client.id)] = client
        return client

    async def find_by_id(self, client_id: str) -> Optional[Client]:
        return self.storage.get(client_id)

    async def find_by_cpf(self, cpf: str) -> Optional[Client]:
        for client in self.storage.values():
            if client.cpf == cpf:
                return client
        return None

    async def find_by_filters(
        self, search: Optional[str], skip: int = 0, limit: int = 50
    ) -> List[Client]:
        entries = list(self.storage.values())
        if search:
            lowered = search.lower()
            entries = [
                client
                for client in entries
                if lowered in client.nome_completo.lower()
                or lowered in (client.email or '').lower()
                or lowered in client.cpf
            ]
        return entries[skip : skip + limit]

    async def count(self, search: Optional[str] = None) -> int:
        results = await self.find_by_filters(search)
        return len(results)

    async def ensure_indexes(self) -> None:  # pragma: no cover - not needed for in-memory
        return None


@pytest.mark.asyncio
async def test_create_client_success() -> None:
    repository = InMemoryClientRepository()
    service = ClientService(repository)

    dto = ClientCreateDTO(nome_completo="Maria Silva", cpf=VALID_CPF)
    result = await service.create_client(dto)

    assert result["success"] is True
    stored = await repository.find_by_cpf(VALID_CPF)
    assert stored is not None
    assert stored.nome_completo == "Maria Silva"


@pytest.mark.asyncio
async def test_create_client_duplicate_cpf() -> None:
    repository = InMemoryClientRepository()
    service = ClientService(repository)

    dto = ClientCreateDTO(nome_completo="Maria Silva", cpf=VALID_CPF)
    await service.create_client(dto)

    duplicate = await service.create_client(dto)
    assert duplicate["success"] is False
    assert duplicate["error_code"] == "duplicate"


@pytest.mark.asyncio
async def test_sync_from_appointment_creates_client() -> None:
    repository = InMemoryClientRepository()
    service = ClientService(repository)

    appointment = Appointment(
        nome_marca="Marca",
        nome_unidade="Unidade",
        nome_paciente="Ana Paciente",
        data_agendamento=datetime(2025, 5, 10, 9, 0),
        hora_agendamento="09:00",
        status="Confirmado",
        telefone="11999999999",
        cpf=VALID_CPF,
    )

    await service.sync_from_appointment(appointment)

    stored = await repository.find_by_cpf(VALID_CPF)
    assert stored is not None
    assert stored.total_agendamentos == 1
    assert stored.appointment_history[0].nome_paciente == "Ana Paciente"


@pytest.mark.asyncio
async def test_sync_from_appointment_updates_existing_client() -> None:
    repository = InMemoryClientRepository()
    service = ClientService(repository)

    dto = ClientCreateDTO(nome_completo="Ana Paciente", cpf=VALID_CPF)
    create_result = await service.create_client(dto)
    assert create_result["success"] is True

    appointment = Appointment(
        nome_marca="Outra Marca",
        nome_unidade="Outra Unidade",
        nome_paciente="Ana Paciente",
        data_agendamento=datetime(2025, 6, 15, 10, 30),
        hora_agendamento="10:30",
        status="Agendado",
        telefone="1188887777",
        cpf=VALID_CPF,
        observacoes="Consulta de retorno",
    )

    await service.sync_from_appointment(appointment)

    stored = await repository.find_by_cpf(VALID_CPF)
    assert stored is not None
    assert stored.total_agendamentos == 1
    assert stored.telefone == "1188887777"
    assert stored.ultima_marca == "Outra Marca"
    assert stored.appointment_history[0].observacoes == "Consulta de retorno"


@pytest.mark.asyncio
async def test_update_client_success() -> None:
    repository = InMemoryClientRepository()
    service = ClientService(repository)

    create_result = await service.create_client(
        ClientCreateDTO(nome_completo="João Cliente", cpf=VALID_CPF)
    )
    client_id = str(create_result["client"].id)

    update_result = await service.update_client(
        client_id,
        ClientUpdateDTO(email="joao@example.com", telefone="1191112222"),
    )

    assert update_result["success"] is True
    stored = await repository.find_by_id(client_id)
    assert stored is not None
    assert stored.email == "joao@example.com"
    assert stored.telefone == "1191112222"


@pytest.mark.asyncio
async def test_list_clients_with_search() -> None:
    repository = InMemoryClientRepository()
    service = ClientService(repository)

    await service.create_client(ClientCreateDTO(nome_completo="Ana Maria", cpf="39053344705"))
    await service.create_client(ClientCreateDTO(nome_completo="Bruno Costa", cpf=SECOND_VALID_CPF))

    result = await service.list_clients(search="Bruno", page=1, page_size=10)

    assert result["success"] is True
    assert len(result["clients"]) == 1
    assert result["clients"][0].nome_completo == "Bruno Costa"
