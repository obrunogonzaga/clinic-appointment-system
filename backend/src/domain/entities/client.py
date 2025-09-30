"""Domain entity representing a clinic client/patient."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.domain.base import Entity
from src.domain.utils.cpf import is_valid_cpf, normalize_cpf


class AppointmentHistoryEntry(BaseModel):
    """Snapshot of an appointment associated with a client."""

    appointment_id: UUID = Field(..., description="Identificador do agendamento")
    nome_marca: Optional[str] = Field(
        None, description="Marca/Clínica utilizada no agendamento"
    )
    nome_unidade: Optional[str] = Field(
        None, description="Unidade relacionada ao agendamento"
    )
    nome_paciente: Optional[str] = Field(
        None, description="Nome do paciente utilizado no agendamento"
    )
    data_agendamento: Optional[datetime] = Field(
        None, description="Data prevista do atendimento"
    )
    hora_agendamento: Optional[str] = Field(
        None, description="Hora prevista do atendimento"
    )
    status: Optional[str] = Field(
        None, description="Status registrado para o agendamento"
    )
    tipo_consulta: Optional[str] = Field(
        None, description="Tipo de consulta ou serviço"
    )
    observacoes: Optional[str] = Field(
        None, description="Observações associadas ao agendamento"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Momento em que o histórico foi registrado",
    )


class Client(Entity):
    """Client entity storing personal data and appointment history."""

    nome_completo: str = Field(..., description="Nome completo do cliente")
    cpf: str = Field(..., description="CPF do cliente (apenas dígitos)")
    telefone: Optional[str] = Field(
        None, description="Telefone principal de contato"
    )
    email: Optional[str] = Field(None, description="Endereço de e-mail do cliente")
    observacoes: Optional[str] = Field(
        None, description="Observações gerais sobre o cliente"
    )
    numero_convenio: Optional[str] = Field(
        None, description="Número do convênio vinculado"
    )
    nome_convenio: Optional[str] = Field(
        None, description="Nome do convênio vinculado"
    )
    carteira_convenio: Optional[str] = Field(
        None, description="Identificação/carteira do convênio"
    )
    ultima_marca: Optional[str] = Field(
        None, description="Última marca registrada em um agendamento"
    )
    ultima_unidade: Optional[str] = Field(
        None, description="Última unidade utilizada"
    )
    ultima_consulta_tipo: Optional[str] = Field(
        None, description="Tipo da última consulta registrada"
    )
    ultima_consulta_status: Optional[str] = Field(
        None, description="Status do último agendamento"
    )
    ultima_data_agendamento: Optional[datetime] = Field(
        None, description="Data do último agendamento conhecido"
    )
    total_agendamentos: int = Field(
        0, ge=0, description="Quantidade total de agendamentos vinculados"
    )
    appointment_history: List[AppointmentHistoryEntry] = Field(
        default_factory=list,
        description="Histórico de agendamentos associados ao cliente",
    )

    @field_validator("nome_completo")
    @classmethod
    def validate_nome_completo(cls, value: str) -> str:
        """Ensure the client's name is not empty."""

        if not value or not value.strip():
            raise ValueError("Nome do cliente é obrigatório")
        return value.strip()

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        """Normalize and validate CPF value."""

        normalized = normalize_cpf(value)
        if normalized is None or not is_valid_cpf(normalized):
            raise ValueError("CPF inválido. Informe 11 dígitos válidos.")
        return normalized

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, value: Optional[str]) -> Optional[str]:
        """Normalize and validate phone numbers."""

        if value is None:
            return None

        digits = (
            value.strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        if digits and not (10 <= len(digits) <= 11):
            raise ValueError("Telefone deve conter 10 ou 11 dígitos")

        return digits or None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        """Trim email values to avoid stray spaces."""

        if value is None:
            return None

        trimmed = value.strip()
        return trimmed or None
