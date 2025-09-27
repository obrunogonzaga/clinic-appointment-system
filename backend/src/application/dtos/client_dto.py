"""DTOs para operações envolvendo clientes."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.domain.utils import normalize_cpf


class ClientCreateDTO(BaseModel):
    """Dados para criação de um novo cliente."""

    nome: str = Field(..., description="Nome completo do cliente")
    cpf: str = Field(..., description="CPF do cliente (somente dígitos)")
    telefone: Optional[str] = Field(
        None, description="Telefone do cliente (somente dígitos)"
    )
    email: Optional[str] = Field(None, description="Email do cliente")
    observacoes: Optional[str] = Field(None, description="Observações internas")

    @field_validator("cpf", mode="before")
    @classmethod
    def normalize_cpf_value(cls, value: str) -> str:
        normalized = normalize_cpf(value)
        if not normalized or len(normalized) != 11:
            raise ValueError("CPF inválido. Informe 11 dígitos válidos.")
        return normalized

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Nome é obrigatório")
        return value.strip()

    @field_validator("telefone", mode="before")
    @classmethod
    def normalize_phone(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        digits = "".join(filter(str.isdigit, str(value)))
        if digits and len(digits) not in (10, 11):
            raise ValueError("Telefone deve conter 10 ou 11 dígitos")
        return digits if digits else None


class ClientUpdateDTO(BaseModel):
    """Dados para atualização parcial de um cliente."""

    nome: Optional[str] = Field(None, description="Nome completo do cliente")
    telefone: Optional[str] = Field(
        None, description="Telefone do cliente (somente dígitos)"
    )
    email: Optional[str] = Field(None, description="Email do cliente")
    observacoes: Optional[str] = Field(None, description="Observações internas")

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Nome não pode ser vazio")
        return trimmed

    @field_validator("telefone", mode="before")
    @classmethod
    def normalize_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        digits = "".join(filter(str.isdigit, str(value)))
        if digits and len(digits) not in (10, 11):
            raise ValueError("Telefone deve conter 10 ou 11 dígitos")
        return digits if digits else None


class ClientHistoryEntryDTO(BaseModel):
    """Representação de uma entrada no histórico de agendamentos."""

    appointment_id: str
    data_agendamento: Optional[datetime] = None
    hora_agendamento: Optional[str] = None
    status: Optional[str] = None
    nome_unidade: Optional[str] = None
    nome_marca: Optional[str] = None
    created_at: datetime


class ClientResponseDTO(BaseModel):
    """Representação completa de um cliente."""

    id: UUID
    nome: str
    cpf: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None
    total_agendamentos: int
    ultimo_agendamento_em: Optional[datetime] = None
    ultimo_status: Optional[str] = None
    ultima_unidade: Optional[str] = None
    ultima_marca: Optional[str] = None
    historico_agendamentos: List[ClientHistoryEntryDTO]
    created_at: datetime
    updated_at: Optional[datetime] = None


class ClientSummaryDTO(BaseModel):
    """Resumo para listagem de clientes."""

    id: UUID
    nome: str
    cpf: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None
    total_agendamentos: int
    ultimo_agendamento_em: Optional[datetime] = None
    ultimo_status: Optional[str] = None
    ultima_unidade: Optional[str] = None
    ultima_marca: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ClientPaginationDTO(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ClientListResponseDTO(BaseModel):
    """Resposta paginada para listagem de clientes."""

    success: bool
    message: Optional[str] = None
    clients: List[ClientSummaryDTO]
    pagination: ClientPaginationDTO


class ClientDetailResponseDTO(BaseModel):
    """Resposta detalhada com histórico completo."""

    success: bool
    message: Optional[str] = None
    client: Optional[ClientResponseDTO] = None
