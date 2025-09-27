"""Domain entities for client management."""

from datetime import datetime
from typing import List, Optional

from pydantic import Field, field_validator

from src.domain.base import Entity, ValueObject
from src.domain.utils import normalize_cpf


class ClientAppointmentHistoryEntry(ValueObject):
    """Snapshot of an appointment associated with a client."""

    appointment_id: str = Field(..., description="Identificador do agendamento")
    data_agendamento: Optional[datetime] = Field(
        None, description="Data do agendamento"
    )
    hora_agendamento: Optional[str] = Field(
        None, description="Hora do agendamento (HH:MM)"
    )
    status: Optional[str] = Field(None, description="Status atual do agendamento")
    nome_unidade: Optional[str] = Field(None, description="Unidade do agendamento")
    nome_marca: Optional[str] = Field(None, description="Marca/Clínica do agendamento")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Momento em que o vínculo com o cliente foi registrado",
    )


class Client(Entity):
    """Client aggregate with contact information and appointment history."""

    nome: str = Field(..., description="Nome completo do cliente")
    cpf: str = Field(..., description="CPF do cliente apenas com dígitos")
    telefone: Optional[str] = Field(
        None, description="Telefone principal do cliente (apenas dígitos)"
    )
    email: Optional[str] = Field(None, description="Email do cliente")
    observacoes: Optional[str] = Field(None, description="Observações internas")
    total_agendamentos: int = Field(
        0, description="Quantidade total de agendamentos vinculados ao cliente"
    )
    ultimo_agendamento_em: Optional[datetime] = Field(
        None, description="Data do último agendamento"
    )
    ultimo_status: Optional[str] = Field(
        None, description="Status do último agendamento registrado"
    )
    ultima_unidade: Optional[str] = Field(
        None, description="Unidade do último agendamento"
    )
    ultima_marca: Optional[str] = Field(
        None, description="Marca do último agendamento"
    )
    historico_agendamentos: List[ClientAppointmentHistoryEntry] = Field(
        default_factory=list,
        description="Histórico completo de agendamentos associados ao cliente",
    )

    @field_validator("cpf", mode="before")
    @classmethod
    def normalize_cpf_value(cls, value: str) -> str:
        """Ensure CPF is stored with digits only."""
        normalized = normalize_cpf(value)
        if not normalized or len(normalized) != 11:
            raise ValueError("CPF inválido. Informe 11 dígitos válidos.")
        return normalized

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, value: str) -> str:
        """Trim and validate client name."""
        if not value or not value.strip():
            raise ValueError("Nome do cliente é obrigatório")
        return value.strip()

    @field_validator("telefone", mode="before")
    @classmethod
    def normalize_phone(cls, value: Optional[str]) -> Optional[str]:
        """Normalize phone numbers keeping only digits."""
        if not value:
            return None
        digits = "".join(filter(str.isdigit, str(value)))
        if digits and len(digits) not in (10, 11):
            raise ValueError("Telefone deve conter 10 ou 11 dígitos")
        return digits if digits else None
