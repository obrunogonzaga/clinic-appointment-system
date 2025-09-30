"""DTOs for client management."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.dtos.appointment_dto import AppointmentResponseDTO


class ClientCreateDTO(BaseModel):
    """DTO for manual client creation."""

    nome_completo: str = Field(..., description="Nome completo do cliente")
    cpf: str = Field(..., description="CPF do cliente (apenas dígitos ou formatado)")
    telefone: Optional[str] = Field(None, description="Telefone principal do cliente")
    email: Optional[str] = Field(None, description="Email do cliente")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    numero_convenio: Optional[str] = Field(None, description="Número do convênio")
    nome_convenio: Optional[str] = Field(None, description="Nome do convênio")
    carteira_convenio: Optional[str] = Field(None, description="Número da carteira do convênio")


class ClientUpdateDTO(BaseModel):
    """DTO for client updates."""

    nome_completo: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None
    numero_convenio: Optional[str] = None
    nome_convenio: Optional[str] = None
    carteira_convenio: Optional[str] = None


class ClientFilterDTO(BaseModel):
    """DTO for filtering clients list."""

    search: Optional[str] = Field(
        None,
        description="Termo de busca aplicado ao nome do cliente",
    )
    cpf: Optional[str] = Field(None, description="CPF específico para busca")
    page: int = Field(1, ge=1, description="Página atual")
    page_size: int = Field(50, ge=1, le=100, description="Itens por página")


class ClientResponseDTO(BaseModel):
    """DTO representing client data."""

    id: UUID
    nome_completo: str
    cpf: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None
    numero_convenio: Optional[str] = None
    nome_convenio: Optional[str] = None
    carteira_convenio: Optional[str] = None
    appointment_ids: List[str] = []
    appointment_count: int = 0
    last_appointment_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ClientSummaryDTO(ClientResponseDTO):
    """Summary DTO for client listings."""

    pass


class ClientListResponseDTO(BaseModel):
    """DTO for paginated client list."""

    success: bool
    message: Optional[str] = None
    clients: List[ClientSummaryDTO]
    pagination: dict


class ClientDetailResponseDTO(BaseModel):
    """DTO for client detail view including appointment history."""

    success: bool
    message: Optional[str] = None
    client: ClientResponseDTO
    history: List[AppointmentResponseDTO]
