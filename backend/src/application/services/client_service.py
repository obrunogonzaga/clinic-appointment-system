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
from src.domain.entities.client import Client, ConvenioInfo
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
            numero_convenio=self._sanitize_optional_string(
                data.numero_convenio
            ),
            nome_convenio=self._sanitize_optional_string(data.nome_convenio),
            carteira_convenio=self._sanitize_optional_string(
                data.carteira_convenio
            ),
        )

        created = await self.client_repository.create(client)
        return {
            "success": True,
            "message": "Cliente cadastrado com sucesso",
            "client": self._to_response(created),
        }

    async def update_client(
        self, client_id: str, data: ClientUpdateDTO
    ) -> Dict:
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

        for key in (
            "email",
            "observacoes",
            "numero_convenio",
            "nome_convenio",
            "carteira_convenio",
        ):
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

    async def list_clients(
        self, filters: ClientFilterDTO
    ) -> ClientListResponseDTO:
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

        clients = await self.client_repository.list(
            query, skip=skip, limit=filters.page_size
        )
        total = await self.client_repository.count(query)

        total_pages = (total + filters.page_size - 1) // filters.page_size

        summaries = [self._to_response(client) for client in clients]
        return ClientListResponseDTO(
            success=True,
            clients=[
                ClientSummaryDTO(**summary.model_dump())
                for summary in summaries
            ],
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

        appointments_by_id = (
            await self.appointment_repository.find_many_by_ids(
                client.appointment_ids
            )
        )
        appointments_by_cpf = await self.appointment_repository.list_by_cpf(
            client.cpf
        )

        history_map = {
            str(appointment.id): appointment
            for appointment in appointments_by_cpf
        }
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

    async def upsert_from_appointment(
        self, appointment: Appointment
    ) -> Optional[str]:
        """
        Ensure a client exists/updated based on appointment data with smart merging.

        Returns:
            Optional[str]: Client ID if successfully created/updated, None otherwise
        """

        normalized_cpf = normalize_cpf(appointment.cpf)
        if not normalized_cpf or not is_valid_cpf(normalized_cpf):
            return None

        existing = await self.client_repository.find_by_cpf(normalized_cpf)
        appointment_id = str(appointment.id)
        appointment_date = (
            appointment.data_agendamento or appointment.created_at
        )

        telefone = self._sanitize_phone(appointment.telefone)
        observacoes = self._sanitize_optional_string(appointment.observacoes)
        numero_convenio = self._sanitize_optional_string(
            appointment.numero_convenio
        )
        nome_convenio = self._sanitize_optional_string(
            appointment.nome_convenio
        )
        carteira_convenio = self._sanitize_optional_string(
            appointment.carteira_convenio
        )

        # Handle convenio information
        convenio = self._extract_convenio_from_appointment(
            appointment, appointment_date
        )

        if not existing:
            # Create new client
            convenios_list = [convenio] if convenio else []

            client = Client(
                nome_completo=appointment.nome_paciente,
                cpf=normalized_cpf,
                telefone=telefone,
                numero_convenio=numero_convenio,
                nome_convenio=nome_convenio,
                carteira_convenio=carteira_convenio,
                convenios_historico=convenios_list,
                observacoes=observacoes,
                appointment_ids=[appointment_id],
                last_appointment_at=appointment_date,
                last_address=appointment.endereco_completo,
                last_address_normalized=appointment.endereco_normalizado,
            )

            existing, created = await self.client_repository.get_or_create(
                client
            )
            if created:
                return str(existing.id)

        if existing is None:
            return None

        # Update existing client with smart merge
        updates: Dict[str, Optional[str]] = {}

        # Only update name and phone if appointment is more recent
        is_more_recent = not existing.last_appointment_at or (
            appointment_date
            and appointment_date >= existing.last_appointment_at
        )

        if is_more_recent:
            name = self._sanitize_required_string(appointment.nome_paciente)
            if name and name != existing.nome_completo:
                updates["nome_completo"] = name

            if telefone and telefone != existing.telefone:
                updates["telefone"] = telefone

        # Update observacoes if present (append or replace)
        if observacoes and observacoes != existing.observacoes:
            updates["observacoes"] = observacoes

        if updates:
            await self.client_repository.update(str(existing.id), updates)

        # Add or update convenio in history
        if convenio:
            await self.client_repository.upsert_convenio(
                str(existing.id), convenio
            )

        # Update last appointment metadata
        last_reference: Optional[datetime] = None
        last_address: Optional[str] = None
        last_address_normalized = None

        if is_more_recent:
            last_reference = appointment_date
            last_address = appointment.endereco_completo
            last_address_normalized = appointment.endereco_normalizado

        await self.client_repository.add_appointment(
            str(existing.id),
            appointment_id,
            last_reference,
            last_address,
            last_address_normalized,
        )

        return str(existing.id)

    def _extract_convenio_from_appointment(
        self, appointment: Appointment, appointment_date: Optional[datetime]
    ) -> Optional[ConvenioInfo]:
        """Extract convenio information from appointment."""

        numero = self._sanitize_optional_string(appointment.numero_convenio)
        nome = self._sanitize_optional_string(appointment.nome_convenio)
        carteira = self._sanitize_optional_string(
            appointment.carteira_convenio
        )

        # If no convenio data, treat as "Particular"
        if not numero and not nome and not carteira:
            nome = "Particular"

        # Only create ConvenioInfo if there's at least a name
        if not nome:
            return None

        return ConvenioInfo(
            numero_convenio=numero,
            nome_convenio=nome,
            carteira_convenio=carteira,
            primeira_utilizacao=appointment_date,
            ultima_utilizacao=appointment_date,
        )

    async def bulk_upsert_from_appointments(
        self, appointments: List[Appointment]
    ) -> None:
        """Bulk upsert clients from appointments."""
        success_count = 0
        skip_count = 0
        error_count = 0

        for appointment in appointments:
            try:
                result = await self.upsert_from_appointment(appointment)
                if result:
                    success_count += 1
                else:
                    skip_count += 1
                    logger.debug(
                        "Skipped client sync for appointment %s (invalid/missing CPF)",
                        appointment.id,
                    )
            except Exception as exc:  # pragma: no cover - defensive logging
                error_count += 1
                logger.warning(
                    "Failed to sync client from appointment %s: %s",
                    appointment.id,
                    exc,
                    exc_info=True,
                )

        logger.info(
            "Bulk client sync complete: %d created/updated, %d skipped, %d errors",
            success_count,
            skip_count,
            error_count,
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
