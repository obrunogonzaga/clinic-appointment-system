"""Data transfer objects for client management."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.dtos.appointment_dto import PaginationDTO


class ClientAppointmentHistoryDTO(BaseModel):
    """DTO representing a single appointment entry in the client history."""

    appointment_id: UUID
    nome_marca: Optional[str] = None
    nome_unidade: Optional[str] = None
    nome_paciente: Optional[str] = None
    data_agendamento: Optional[datetime] = None
    hora_agendamento: Optional[str] = None
    status: Optional[str] = None
    tipo_consulta: Optional[str] = None
    observacoes: Optional[str] = None
    created_at: datetime


class ClientSummaryDTO(BaseModel):
    """Compact representation for listing clients."""

    id: UUID
    nome_completo: str
    cpf: str
    cpf_formatado: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    total_agendamentos: int
    ultima_data_agendamento: Optional[datetime] = None
    ultima_unidade: Optional[str] = None
    ultima_marca: Optional[str] = None
    ultima_consulta_tipo: Optional[str] = None
    ultima_consulta_status: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ClientDetailDTO(ClientSummaryDTO):
    """Detailed representation including history."""

    observacoes: Optional[str] = None
    numero_convenio: Optional[str] = None
    nome_convenio: Optional[str] = None
    carteira_convenio: Optional[str] = None
    appointment_history: List[ClientAppointmentHistoryDTO] = Field(default_factory=list)


class ClientCreateDTO(BaseModel):
    """Payload for creating a new client manually."""

    nome_completo: str = Field(..., min_length=1)
    cpf: str = Field(..., min_length=11, max_length=20)
    telefone: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    observacoes: Optional[str] = Field(default=None)
    numero_convenio: Optional[str] = Field(default=None)
    nome_convenio: Optional[str] = Field(default=None)
    carteira_convenio: Optional[str] = Field(default=None)


class ClientUpdateDTO(BaseModel):
    """Payload for updating existing clients."""

    nome_completo: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None
    numero_convenio: Optional[str] = None
    nome_convenio: Optional[str] = None
    carteira_convenio: Optional[str] = None


class ClientResponseDTO(BaseModel):
    """Response wrapper for single client operations."""

    success: bool
    message: Optional[str] = None
    client: ClientDetailDTO


class ClientListResponseDTO(BaseModel):
    """Response for listing clients with pagination."""

    success: bool
    message: Optional[str] = None
    clients: List[ClientSummaryDTO]
    pagination: PaginationDTO
