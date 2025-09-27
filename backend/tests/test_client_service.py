import pytest

from src.application.services.client_service import ClientService
from src.domain.entities.appointment import Appointment
from src.domain.entities.client import Client, ClientAppointmentHistoryEntry
from src.domain.repositories.client_repository_interface import ClientRepositoryInterface


class InMemoryClientRepository(ClientRepositoryInterface):
    def __init__(self) -> None:
        self.storage: dict[str, Client] = {}

    async def ensure_indexes(self) -> None:  # pragma: no cover - not needed for memory repo
        return None

    async def create(self, client: Client) -> Client:
        self.storage[str(client.id)] = client
        return client

    async def update(self, client: Client) -> Client:
        self.storage[str(client.id)] = client
        return client

    async def find_by_id(self, client_id: str) -> Client | None:
        return self.storage.get(client_id)

    async def find_by_cpf(self, cpf: str) -> Client | None:
        for client in self.storage.values():
            if client.cpf == cpf:
                return client
        return None

    async def list_clients(self, search=None, skip: int = 0, limit: int = 50):
        clients = list(self.storage.values())
        return clients[skip : skip + limit], len(clients)

    async def append_history_entry(self, client_id: str, entry: ClientAppointmentHistoryEntry) -> None:
        client = self.storage.get(client_id)
        if not client:
            return
        if not any(item.appointment_id == entry.appointment_id for item in client.historico_agendamentos):
            client.historico_agendamentos.append(entry)
            client.total_agendamentos += 1
            self.storage[client_id] = client


@pytest.mark.asyncio
async def test_sync_from_appointment_creates_client() -> None:
    repository = InMemoryClientRepository()
    service = ClientService(repository)

    appointment = Appointment(
        nome_marca='Marca',
        nome_unidade='Unidade',
        nome_paciente='Paciente Teste',
        telefone='11999999999',
        status='Confirmado',
        cpf='12345678901',
    )

    await service.sync_from_appointment(appointment)

    created = await repository.find_by_cpf('12345678901')
    assert created is not None
    assert created.nome == 'Paciente Teste'
    assert created.total_agendamentos == 1
    assert len(created.historico_agendamentos) == 1


@pytest.mark.asyncio
async def test_sync_from_appointment_updates_existing_client() -> None:
    repository = InMemoryClientRepository()
    existing = Client(
        nome='Nome Original',
        cpf='12345678901',
        telefone='11988887777',
        total_agendamentos=1,
        historico_agendamentos=[
            ClientAppointmentHistoryEntry(
                appointment_id='existing',
                status='Pendente',
            )
        ],
    )
    await repository.create(existing)
    service = ClientService(repository)

    appointment = Appointment(
        nome_marca='Marca',
        nome_unidade='Unidade',
        nome_paciente='Paciente Atualizado',
        telefone='21900001111',
        status='Confirmado',
        cpf='12345678901',
    )

    await service.sync_from_appointment(appointment)

    updated = await repository.find_by_cpf('12345678901')
    assert updated is not None
    assert updated.nome == 'Paciente Atualizado'
    assert updated.telefone == '21900001111'
    assert updated.total_agendamentos == 2
    assert any(item.appointment_id == str(appointment.id) for item in updated.historico_agendamentos)
