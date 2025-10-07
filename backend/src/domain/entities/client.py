"""Client entity representing patients/customers for appointments."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from src.domain.base import Entity
from src.domain.utils import is_valid_cpf, normalize_cpf


class ConvenioInfo(BaseModel):
    """Information about a health insurance plan used by the client."""

    numero_convenio: Optional[str] = Field(
        None, description="Número do convênio"
    )
    nome_convenio: Optional[str] = Field(None, description="Nome do convênio")
    carteira_convenio: Optional[str] = Field(
        None, description="Número da carteira do convênio"
    )
    primeira_utilizacao: Optional[datetime] = Field(
        None,
        description="Data da primeira vez que este convênio foi registrado",
    )
    ultima_utilizacao: Optional[datetime] = Field(
        None, description="Data da última vez que este convênio foi utilizado"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "numero_convenio": "12345",
                "nome_convenio": "Unimed",
                "carteira_convenio": "A123456",
                "primeira_utilizacao": "2024-01-15T14:30:00",
                "ultima_utilizacao": "2024-05-20T10:00:00",
            }
        }


class Client(Entity):
    """Client entity storing patient contact and tracking information."""

    nome_completo: str = Field(..., description="Nome completo do cliente")
    cpf: str = Field(..., description="CPF do cliente (apenas dígitos)")

    telefone: Optional[str] = Field(
        None, description="Telefone principal do cliente"
    )
    email: Optional[str] = Field(None, description="Email para contato")
    observacoes: Optional[str] = Field(
        None, description="Observações gerais sobre o cliente"
    )

    # Campos DEPRECATED - mantidos por compatibilidade, use convenios_historico
    numero_convenio: Optional[str] = Field(
        None, description="[DEPRECATED] Número do convênio do cliente"
    )
    nome_convenio: Optional[str] = Field(
        None, description="[DEPRECATED] Nome do convênio do cliente"
    )
    carteira_convenio: Optional[str] = Field(
        None, description="[DEPRECATED] Número da carteira do convênio"
    )

    # Novo modelo de convênios (suporta múltiplos convênios)
    convenios_historico: List[ConvenioInfo] = Field(
        default_factory=list,
        description="Histórico de todos os convênios utilizados pelo cliente",
    )

    appointment_ids: List[str] = Field(
        default_factory=list,
        description="Lista de IDs de agendamentos relacionados ao cliente",
    )
    last_appointment_at: Optional[datetime] = Field(
        None, description="Data/hora do último agendamento conhecido"
    )

    # Endereço do último agendamento
    last_address: Optional[str] = Field(
        None, description="Endereço completo do último agendamento"
    )
    last_address_normalized: Optional[Dict[str, Optional[str]]] = Field(
        None, description="Endereço normalizado do último agendamento"
    )

    @field_validator("nome_completo")
    @classmethod
    def validate_nome_completo(cls, value: str) -> str:
        """Ensure the customer name has content."""

        if not value or not value.strip():
            raise ValueError("Nome do cliente é obrigatório")
        return value.strip()

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        """Normalize and validate CPF."""

        normalized = normalize_cpf(value)
        if not normalized or not is_valid_cpf(normalized):
            raise ValueError("CPF inválido")
        return normalized

    @field_validator("telefone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """Normalize phone numbers keeping digits only."""

        if value is None:
            return None

        digits = "".join(char for char in value if char.isdigit())
        if digits and len(digits) not in (10, 11):
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")
        return digits or None

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "ae0d94e5-2fb6-4e2e-9b35-812a4f821234",
                "nome_completo": "João da Silva",
                "cpf": "12345678901",
                "telefone": "11999998888",
                "email": "joao.silva@email.com",
                "numero_convenio": "12345",
                "nome_convenio": "Unimed",
                "carteira_convenio": "A123456",
                "convenios_historico": [
                    {
                        "numero_convenio": "12345",
                        "nome_convenio": "Unimed",
                        "carteira_convenio": "A123456",
                        "primeira_utilizacao": "2024-01-15T14:30:00",
                        "ultima_utilizacao": "2024-03-20T10:00:00",
                    },
                    {
                        "numero_convenio": None,
                        "nome_convenio": "Particular",
                        "carteira_convenio": None,
                        "primeira_utilizacao": "2024-04-10T09:00:00",
                        "ultima_utilizacao": "2024-05-01T12:00:00",
                    },
                ],
                "appointment_ids": [
                    "c6a6c672-7ce3-4a0f-a50a-0f2a746f8f4d",
                    "9ec8a4c6-44ec-4f2f-8db6-725243404abc",
                ],
                "last_appointment_at": "2024-05-01T12:00:00",
                "last_address": "Rua das Flores, 123, Centro, São Paulo, SP",
                "last_address_normalized": {
                    "rua": "Rua das Flores",
                    "numero": "123",
                    "complemento": None,
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "cep": "01234-567",
                },
                "created_at": "2024-04-10T09:30:00",
                "updated_at": "2024-05-01T12:30:00",
            }
        }
