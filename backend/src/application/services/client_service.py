"""Serviços de aplicação relacionados a clientes."""

from math import ceil
from typing import Dict, List, Optional

from src.application.dtos.client_dto import (
    ClientCreateDTO,
    ClientDetailResponseDTO,
    ClientListResponseDTO,
    ClientResponseDTO,
    ClientSummaryDTO,
    ClientUpdateDTO,
)
from src.domain.entities.appointment import Appointment
from src.domain.entities.client import Client, ClientAppointmentHistoryEntry
from src.domain.repositories.client_repository_interface import (
    ClientRepositoryInterface,
)


class ClientService:
    """Orquestra regras de negócio para o gerenciamento de clientes."""

    def __init__(self, repository: ClientRepositoryInterface) -> None:
        self.repository = repository

    async def list_clients(
        self, search: Optional[str] = None, page: int = 1, page_size: int = 50
    ) -> ClientListResponseDTO:
        """List clients with optional search and pagination."""

        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 1

        skip = (page - 1) * page_size
        clients, total = await self.repository.list_clients(
            search=search, skip=skip, limit=page_size
        )

        total_pages = ceil(total / page_size) if page_size else 1
        pagination = {
            "page": page,
            "page_size": page_size,
            "total_items": total,
            "total_pages": max(total_pages, 1),
            "has_next": page * page_size < total,
            "has_previous": page > 1,
        }

        summaries = [
            ClientSummaryDTO(**client.model_dump()) for client in clients
        ]

        return ClientListResponseDTO(
            success=True,
            clients=summaries,
            pagination=pagination,
        )

    async def create_client(self, data: ClientCreateDTO) -> Dict:
        """Register a new client if CPF is not already in use."""

        existing = await self.repository.find_by_cpf(data.cpf)
        if existing:
            return {
                "success": False,
                "message": "CPF já cadastrado para outro cliente.",
                "error_code": "duplicate",
            }

        client = Client(
            nome=data.nome,
            cpf=data.cpf,
            telefone=data.telefone,
            email=data.email,
            observacoes=data.observacoes,
        )

        created = await self.repository.create(client)
        return {
            "success": True,
            "message": "Cliente cadastrado com sucesso.",
            "client": ClientResponseDTO(**created.model_dump()),
        }

    async def update_client(self, client_id: str, data: ClientUpdateDTO) -> Dict:
        """Update existing client fields."""

        client = await self.repository.find_by_id(client_id)
        if not client:
            return {
                "success": False,
                "message": "Cliente não encontrado.",
                "error_code": "not_found",
            }

        if data.nome is not None:
            client.nome = data.nome
        if data.telefone is not None:
            client.telefone = data.telefone
        if data.email is not None:
            client.email = data.email
        if data.observacoes is not None:
            client.observacoes = data.observacoes

        client.mark_as_updated()
        updated = await self.repository.update(client)
        return {
            "success": True,
            "message": "Cliente atualizado com sucesso.",
            "client": ClientResponseDTO(**updated.model_dump()),
        }

    async def get_client_detail(self, client_id: str) -> ClientDetailResponseDTO:
        """Fetch detailed information for a client."""

        client = await self.repository.find_by_id(client_id)
        if not client:
            return ClientDetailResponseDTO(
                success=False,
                message="Cliente não encontrado.",
                client=None,  # type: ignore[arg-type]
            )

        return ClientDetailResponseDTO(
            success=True,
            client=ClientResponseDTO(**client.model_dump()),
        )

    async def sync_from_appointment(self, appointment: Appointment) -> None:
        """Create or update client data based on an appointment."""

        if not appointment.cpf:
            return

        existing = await self.repository.find_by_cpf(appointment.cpf)
        history_entry = ClientAppointmentHistoryEntry(
            appointment_id=str(appointment.id),
            data_agendamento=appointment.data_agendamento,
            hora_agendamento=appointment.hora_agendamento,
            status=appointment.status,
            nome_unidade=appointment.nome_unidade,
            nome_marca=appointment.nome_marca,
            created_at=appointment.created_at,
        )

        if existing:
            updated_history = False
            for entry in existing.historico_agendamentos:
                if entry.appointment_id == history_entry.appointment_id:
                    entry.data_agendamento = history_entry.data_agendamento
                    entry.hora_agendamento = history_entry.hora_agendamento
                    entry.status = history_entry.status
                    entry.nome_unidade = history_entry.nome_unidade
                    entry.nome_marca = history_entry.nome_marca
                    updated_history = True
                    break

            if not updated_history:
                existing.historico_agendamentos.append(history_entry)
                existing.total_agendamentos += 1

            existing.nome = appointment.nome_paciente
            if appointment.telefone:
                existing.telefone = appointment.telefone
            existing.ultimo_agendamento_em = (
                appointment.data_agendamento or existing.ultimo_agendamento_em
            )
            existing.ultimo_status = appointment.status or existing.ultimo_status
            existing.ultima_unidade = (
                appointment.nome_unidade or existing.ultima_unidade
            )
            existing.ultima_marca = appointment.nome_marca or existing.ultima_marca
            existing.mark_as_updated()
            await self.repository.update(existing)
            return

        client = Client(
            nome=appointment.nome_paciente,
            cpf=appointment.cpf,
            telefone=appointment.telefone,
            total_agendamentos=1,
            ultimo_agendamento_em=appointment.data_agendamento,
            ultimo_status=appointment.status,
            ultima_unidade=appointment.nome_unidade,
            ultima_marca=appointment.nome_marca,
            historico_agendamentos=[history_entry],
        )
        await self.repository.create(client)

    async def sync_from_appointments(self, appointments: List[Appointment]) -> None:
        """Sync clients for a batch of appointments."""

        for appointment in appointments:
            await self.sync_from_appointment(appointment)
