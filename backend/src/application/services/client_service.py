"""Service responsible for client management operations."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from src.application.dtos.appointment_dto import AppointmentResponseDTO
from src.application.dtos.client_dto import (
    ClientCreateDTO,
    ClientDetailResponseDTO,
    ClientFilterDTO,
    ClientListResponseDTO,
    ClientResponseDTO,
    ClientSummaryDTO,
    ClientUpdateDTO,
)
from src.domain.entities.appointment import Appointment
from src.domain.entities.client import Client
from src.domain.repositories.appointment_repository_interface import (
    AppointmentRepositoryInterface,
)
from src.domain.repositories.client_repository_interface import (
    ClientRepositoryInterface,
)
from src.domain.utils import is_valid_cpf, normalize_cpf


logger = logging.getLogger(__name__)


class ClientService:
    """Business logic related to clients."""

    def __init__(
        self,
        client_repository: ClientRepositoryInterface,
        appointment_repository: AppointmentRepositoryInterface,
    ) -> None:
        self.client_repository = client_repository
        self.appointment_repository = appointment_repository

    async def create_client(self, data: ClientCreateDTO) -> Dict:
        """Create a client manually from the management screen."""

        normalized_cpf = normalize_cpf(data.cpf)
        if not normalized_cpf or not is_valid_cpf(normalized_cpf):
            return {
                "success": False,
                "message": "CPF inválido",
                "field": "cpf",
            }

        existing = await self.client_repository.find_by_cpf(normalized_cpf)
        if existing:
            return {
                "success": False,
                "message": "CPF já cadastrado no sistema",
                "field": "cpf",
            }

        client = Client(
            nome_completo=data.nome_completo,
            cpf=normalized_cpf,
            telefone=self._sanitize_phone(data.telefone),
            email=self._sanitize_optional_string(data.email),
            observacoes=self._sanitize_optional_string(data.observacoes),
            numero_convenio=self._sanitize_optional_string(data.numero_convenio),
            nome_convenio=self._sanitize_optional_string(data.nome_convenio),
            carteira_convenio=self._sanitize_optional_string(data.carteira_convenio),
        )

        created = await self.client_repository.create(client)
        return {
            "success": True,
            "message": "Cliente cadastrado com sucesso",
            "client": self._to_response(created),
        }

    async def update_client(self, client_id: str, data: ClientUpdateDTO) -> Dict:
        """Update client information."""

        existing = await self.client_repository.find_by_id(client_id)
        if not existing:
            return {
                "success": False,
                "message": "Cliente não encontrado",
            }

        payload = data.model_dump(exclude_unset=True)
        if not payload:
            return {
                "success": True,
                "message": "Nenhuma alteração realizada",
                "client": self._to_response(existing),
            }

        updates: Dict[str, Optional[str]] = {}
        if "nome_completo" in payload:
            name = self._sanitize_required_string(payload["nome_completo"])
            updates["nome_completo"] = name

        if "telefone" in payload:
            updates["telefone"] = self._sanitize_phone(payload["telefone"])

        for key in ("email", "observacoes", "numero_convenio", "nome_convenio", "carteira_convenio"):
            if key in payload:
                updates[key] = self._sanitize_optional_string(payload[key])

        updated = await self.client_repository.update(client_id, updates)
        if not updated:
            return {
                "success": False,
                "message": "Erro ao atualizar cliente",
            }

        return {
            "success": True,
            "message": "Cliente atualizado com sucesso",
            "client": self._to_response(updated),
        }

    async def list_clients(self, filters: ClientFilterDTO) -> ClientListResponseDTO:
        """Return paginated list of clients respecting filters."""

        skip = (filters.page - 1) * filters.page_size
        query: Dict[str, object] = {}

        if filters.search:
            query["nome_completo"] = {
                "$regex": filters.search,
                "$options": "i",
            }

        if filters.cpf:
            normalized = normalize_cpf(filters.cpf)
            if normalized:
                query["cpf"] = normalized
            else:
                # When CPF filter is invalid digits, the result is empty
                return ClientListResponseDTO(
                    success=True,
                    message="Nenhum cliente encontrado",
                    clients=[],
                    pagination={
                        "page": filters.page,
                        "page_size": filters.page_size,
                        "total_items": 0,
                        "total_pages": 0,
                        "has_next": False,
                        "has_previous": False,
                    },
                )

        clients = await self.client_repository.list(query, skip=skip, limit=filters.page_size)
        total = await self.client_repository.count(query)

        total_pages = (total + filters.page_size - 1) // filters.page_size

        summaries = [self._to_response(client) for client in clients]
        return ClientListResponseDTO(
            success=True,
            clients=[ClientSummaryDTO(**summary.model_dump()) for summary in summaries],
            pagination={
                "page": filters.page,
                "page_size": filters.page_size,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": filters.page < total_pages,
                "has_previous": filters.page > 1,
            },
        )

    async def get_client_detail(self, client_id: str) -> Dict:
        """Retrieve client detail including appointment history."""

        client = await self.client_repository.find_by_id(client_id)
        if not client:
            return {
                "success": False,
                "message": "Cliente não encontrado",
            }

        appointments_by_id = await self.appointment_repository.find_many_by_ids(
            client.appointment_ids
        )
        appointments_by_cpf = await self.appointment_repository.list_by_cpf(client.cpf)

        history_map = {str(appointment.id): appointment for appointment in appointments_by_cpf}
        for appointment in appointments_by_id:
            history_map[str(appointment.id)] = appointment

        history = [
            AppointmentResponseDTO(**appointment.model_dump())
            for appointment in sorted(
                history_map.values(),
                key=lambda item: (
                    item.data_agendamento or item.created_at,
                    item.created_at,
                ),
                reverse=True,
            )
        ]

        return ClientDetailResponseDTO(
            success=True,
            client=self._to_response(client),
            history=history,
        ).model_dump()

    async def upsert_from_appointment(self, appointment: Appointment) -> None:
        """Ensure a client exists/updated based on appointment data."""

        normalized_cpf = normalize_cpf(appointment.cpf)
        if not normalized_cpf or not is_valid_cpf(normalized_cpf):
            return

        existing = await self.client_repository.find_by_cpf(normalized_cpf)
        appointment_id = str(appointment.id)
        appointment_date = appointment.data_agendamento or appointment.created_at

        if not existing:
            client = Client(
                nome_completo=appointment.nome_paciente,
                cpf=normalized_cpf,
                telefone=self._sanitize_phone(appointment.telefone),
                numero_convenio=self._sanitize_optional_string(
                    appointment.numero_convenio
                ),
                nome_convenio=self._sanitize_optional_string(
                    appointment.nome_convenio
                ),
                carteira_convenio=self._sanitize_optional_string(
                    appointment.carteira_convenio
                ),
                observacoes=self._sanitize_optional_string(appointment.observacoes),
                appointment_ids=[appointment_id],
                last_appointment_at=appointment_date,
            )

            await self.client_repository.create(client)
            return

        updates: Dict[str, Optional[str]] = {}

        name = self._sanitize_required_string(appointment.nome_paciente)
        if name and name != existing.nome_completo:
            updates["nome_completo"] = name

        phone = self._sanitize_phone(appointment.telefone)
        if phone and phone != existing.telefone:
            updates["telefone"] = phone

        for key in ("numero_convenio", "nome_convenio", "carteira_convenio", "observacoes"):
            value = getattr(appointment, key, None)
            sanitized = self._sanitize_optional_string(value)
            if sanitized and sanitized != getattr(existing, key):
                updates[key] = sanitized

        if updates:
            await self.client_repository.update(str(existing.id), updates)

        last_reference: Optional[datetime] = appointment_date
        if existing.last_appointment_at and last_reference:
            if existing.last_appointment_at >= last_reference:
                last_reference = None

        await self.client_repository.add_appointment(
            str(existing.id), appointment_id, last_reference
        )

    async def bulk_upsert_from_appointments(
        self, appointments: List[Appointment]
    ) -> None:
        for appointment in appointments:
            try:
                await self.upsert_from_appointment(appointment)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning(
                    "Failed to sync client from appointment %s: %s",
                    appointment.id,
                    exc,
                )

    def _to_response(self, client: Client) -> ClientResponseDTO:
        payload = client.model_dump()
        payload["appointment_count"] = len(client.appointment_ids)
        return ClientResponseDTO(**payload)

    @staticmethod
    def _sanitize_phone(value: Optional[str]) -> Optional[str]:
        if not value:
            return None

        digits = "".join(filter(str.isdigit, value))
        return digits or None

    @staticmethod
    def _sanitize_optional_string(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @staticmethod
    def _sanitize_required_string(value: Optional[str]) -> str:
        if not value:
            return ""
        return value.strip()
