"""Service layer for client management and synchronization."""

from __future__ import annotations

from typing import Dict, List, Optional

from src.application.dtos.client_dto import (
    ClientAppointmentHistoryDTO,
    ClientCreateDTO,
    ClientDetailDTO,
    ClientResponseDTO,
    ClientSummaryDTO,
    ClientUpdateDTO,
)
from src.application.dtos.appointment_dto import PaginationDTO
from src.domain.entities.appointment import Appointment
from src.domain.entities.client import AppointmentHistoryEntry, Client
from src.domain.repositories.client_repository_interface import (
    ClientRepositoryInterface,
)
from src.domain.utils.cpf import format_cpf, is_valid_cpf, normalize_cpf


class ClientService:
    """Application service responsible for client operations."""

    def __init__(self, client_repository: ClientRepositoryInterface):
        self.client_repository = client_repository

    async def create_client(self, payload: ClientCreateDTO) -> Dict:
        """Create a client manually from the management screen."""

        try:
            cpf = normalize_cpf(payload.cpf)
            if cpf is None or not is_valid_cpf(cpf):
                return {
                    "success": False,
                    "message": "CPF inválido. Informe 11 dígitos válidos.",
                    "error_code": "validation",
                }

            existing = await self.client_repository.find_by_cpf(cpf)
            if existing:
                return {
                    "success": False,
                    "message": "Já existe um cliente cadastrado com este CPF.",
                    "error_code": "duplicate",
                }

            client = Client(
                nome_completo=payload.nome_completo,
                cpf=cpf,
                telefone=self._normalize_phone(payload.telefone),
                email=self._sanitize_text(payload.email),
                observacoes=self._sanitize_text(payload.observacoes),
                numero_convenio=self._sanitize_text(payload.numero_convenio),
                nome_convenio=self._sanitize_text(payload.nome_convenio),
                carteira_convenio=self._sanitize_text(payload.carteira_convenio),
            )
            self._refresh_last_appointment(client)

            created = await self.client_repository.create(client)

            return {
                "success": True,
                "message": "Cliente cadastrado com sucesso.",
                "client": self._to_detail_dto(created),
            }
        except ValueError as exc:
            return {
                "success": False,
                "message": str(exc),
                "error_code": "validation",
            }
        except Exception as exc:  # pragma: no cover - defensive branch
            return {
                "success": False,
                "message": f"Erro ao criar cliente: {str(exc)}",
                "error_code": "internal",
            }

    async def update_client(self, client_id: str, payload: ClientUpdateDTO) -> Dict:
        """Update editable fields for an existing client."""

        try:
            client = await self.client_repository.find_by_id(client_id)
            if not client:
                return {
                    "success": False,
                    "message": "Cliente não encontrado.",
                    "error_code": "not_found",
                }

            updates = payload.model_dump(exclude_unset=True)
            if not updates:
                return {
                    "success": True,
                    "message": "Nenhuma alteração realizada.",
                    "client": self._to_detail_dto(client),
                }

            if "nome_completo" in updates and updates["nome_completo"]:
                client.nome_completo = updates["nome_completo"]

            if "telefone" in updates:
                client.telefone = self._normalize_phone(updates["telefone"])

            if "email" in updates:
                client.email = self._sanitize_text(updates["email"])

            if "observacoes" in updates:
                client.observacoes = self._sanitize_text(updates["observacoes"])

            if "numero_convenio" in updates:
                client.numero_convenio = self._sanitize_text(updates["numero_convenio"])

            if "nome_convenio" in updates:
                client.nome_convenio = self._sanitize_text(updates["nome_convenio"])

            if "carteira_convenio" in updates:
                client.carteira_convenio = self._sanitize_text(updates["carteira_convenio"])

            client.mark_as_updated()
            saved = await self.client_repository.update(client)

            return {
                "success": True,
                "message": "Cliente atualizado com sucesso.",
                "client": self._to_detail_dto(saved),
            }
        except ValueError as exc:
            return {
                "success": False,
                "message": str(exc),
                "error_code": "validation",
            }
        except Exception as exc:  # pragma: no cover - defensive branch
            return {
                "success": False,
                "message": f"Erro ao atualizar cliente: {str(exc)}",
                "error_code": "internal",
            }

    async def list_clients(
        self, search: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> Dict:
        """List clients with pagination support."""

        skip = (page - 1) * page_size
        clients = await self.client_repository.find_by_filters(search, skip, page_size)
        total = await self.client_repository.count(search)

        total_pages = max((total + page_size - 1) // page_size, 1)
        pagination = PaginationDTO(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

        return {
            "success": True,
            "clients": [self._to_summary_dto(client) for client in clients],
            "pagination": pagination,
        }

    async def get_client(self, client_id: str) -> Dict:
        """Retrieve a client by identifier."""

        client = await self.client_repository.find_by_id(client_id)
        if not client:
            return {
                "success": False,
                "message": "Cliente não encontrado.",
                "error_code": "not_found",
            }

        return {
            "success": True,
            "client": self._to_detail_dto(client),
        }

    async def sync_from_appointment(self, appointment: Appointment) -> None:
        """Ensure the client record reflects information from the appointment."""

        cpf_candidates = [
            appointment.cpf,
            (appointment.documento_normalizado or {}).get("cpf")
            if appointment.documento_normalizado
            else None,
        ]

        cpf_value: Optional[str] = None
        for candidate in cpf_candidates:
            normalized = normalize_cpf(candidate)
            if normalized and is_valid_cpf(normalized):
                cpf_value = normalized
                break

        if not cpf_value:
            return

        history_entry = AppointmentHistoryEntry(
            appointment_id=appointment.id,
            nome_marca=appointment.nome_marca,
            nome_unidade=appointment.nome_unidade,
            nome_paciente=appointment.nome_paciente,
            data_agendamento=appointment.data_agendamento,
            hora_agendamento=appointment.hora_agendamento,
            status=appointment.status,
            tipo_consulta=appointment.tipo_consulta,
            observacoes=appointment.observacoes,
            created_at=appointment.created_at,
        )

        client = await self.client_repository.find_by_cpf(cpf_value)
        if client is None:
            client = Client(
                nome_completo=appointment.nome_paciente,
                cpf=cpf_value,
                telefone=appointment.telefone,
                observacoes=appointment.observacoes,
                numero_convenio=appointment.numero_convenio,
                nome_convenio=appointment.nome_convenio,
                carteira_convenio=appointment.carteira_convenio,
                appointment_history=[history_entry],
            )
            self._refresh_last_appointment(client)
            await self.client_repository.create(client)
            return

        updated = False

        if appointment.nome_paciente and appointment.nome_paciente != client.nome_completo:
            client.nome_completo = appointment.nome_paciente
            updated = True

        if appointment.telefone and appointment.telefone != client.telefone:
            client.telefone = appointment.telefone
            updated = True

        if appointment.observacoes and appointment.observacoes != client.observacoes:
            client.observacoes = appointment.observacoes
            updated = True

        if appointment.numero_convenio and (
            appointment.numero_convenio != client.numero_convenio
        ):
            client.numero_convenio = appointment.numero_convenio
            updated = True

        if appointment.nome_convenio and (
            appointment.nome_convenio != client.nome_convenio
        ):
            client.nome_convenio = appointment.nome_convenio
            updated = True

        if appointment.carteira_convenio and (
            appointment.carteira_convenio != client.carteira_convenio
        ):
            client.carteira_convenio = appointment.carteira_convenio
            updated = True

        history_map: Dict[str, AppointmentHistoryEntry] = {
            str(entry.appointment_id): entry for entry in client.appointment_history
        }

        entry_key = str(history_entry.appointment_id)
        current_entry = history_map.get(entry_key)
        if current_entry is None:
            client.appointment_history.append(history_entry)
            updated = True
        elif current_entry != history_entry:
            history_map[entry_key] = history_entry
            client.appointment_history = list(history_map.values())
            updated = True

        if updated:
            # Keep history sorted by appointment date/creation for consistency
            client.appointment_history = sorted(
                client.appointment_history,
                key=lambda item: item.data_agendamento or item.created_at,
            )

        self._refresh_last_appointment(client)

        if updated:
            client.mark_as_updated()
            await self.client_repository.update(client)

    def _normalize_phone(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        digits = "".join(filter(str.isdigit, value))
        return digits or None

    def _sanitize_text(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    def _refresh_last_appointment(self, client: Client) -> None:
        if not client.appointment_history:
            client.total_agendamentos = 0
            client.ultima_data_agendamento = None
            client.ultima_unidade = None
            client.ultima_marca = None
            client.ultima_consulta_tipo = None
            client.ultima_consulta_status = None
            return

        sorted_history = sorted(
            client.appointment_history,
            key=lambda item: item.data_agendamento or item.created_at,
        )
        client.appointment_history = sorted_history
        client.total_agendamentos = len(sorted_history)

        latest = sorted_history[-1]
        client.ultima_data_agendamento = latest.data_agendamento or latest.created_at
        client.ultima_unidade = latest.nome_unidade
        client.ultima_marca = latest.nome_marca
        client.ultima_consulta_tipo = latest.tipo_consulta
        client.ultima_consulta_status = latest.status

    def _to_summary_dto(self, client: Client) -> ClientSummaryDTO:
        return ClientSummaryDTO(
            id=client.id,
            nome_completo=client.nome_completo,
            cpf=client.cpf,
            cpf_formatado=format_cpf(client.cpf),
            telefone=client.telefone,
            email=client.email,
            total_agendamentos=client.total_agendamentos,
            ultima_data_agendamento=client.ultima_data_agendamento,
            ultima_unidade=client.ultima_unidade,
            ultima_marca=client.ultima_marca,
            ultima_consulta_tipo=client.ultima_consulta_tipo,
            ultima_consulta_status=client.ultima_consulta_status,
            created_at=client.created_at,
            updated_at=client.updated_at,
        )

    def _to_detail_dto(self, client: Client) -> ClientDetailDTO:
        summary = self._to_summary_dto(client)
        history = [
            ClientAppointmentHistoryDTO(**entry.model_dump())
            for entry in client.appointment_history
        ]
        return ClientDetailDTO(
            **summary.model_dump(),
            observacoes=client.observacoes,
            numero_convenio=client.numero_convenio,
            nome_convenio=client.nome_convenio,
            carteira_convenio=client.carteira_convenio,
            appointment_history=history,
        )
