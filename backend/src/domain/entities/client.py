"""Client entity representing patients/customers for appointments."""

from datetime import datetime
from typing import List, Optional

from pydantic import Field, field_validator

from src.domain.base import Entity
from src.domain.utils import is_valid_cpf, normalize_cpf


class Client(Entity):
    """Client entity storing patient contact and tracking information."""

    nome_completo: str = Field(..., description="Nome completo do cliente")
    cpf: str = Field(..., description="CPF do cliente (apenas dígitos)")

    telefone: Optional[str] = Field(None, description="Telefone principal do cliente")
    email: Optional[str] = Field(None, description="Email para contato")
    observacoes: Optional[str] = Field(None, description="Observações gerais sobre o cliente")

    numero_convenio: Optional[str] = Field(None, description="Número do convênio do cliente")
    nome_convenio: Optional[str] = Field(None, description="Nome do convênio do cliente")
    carteira_convenio: Optional[str] = Field(None, description="Número da carteira do convênio")

    appointment_ids: List[str] = Field(
        default_factory=list,
        description="Lista de IDs de agendamentos relacionados ao cliente",
    )
    last_appointment_at: Optional[datetime] = Field(
        None, description="Data/hora do último agendamento conhecido"
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
                "appointment_ids": [
                    "c6a6c672-7ce3-4a0f-a50a-0f2a746f8f4d",
                    "9ec8a4c6-44ec-4f2f-8db6-725243404abc",
                ],
                "last_appointment_at": "2024-05-01T12:00:00",
                "created_at": "2024-04-10T09:30:00",
                "updated_at": "2024-05-01T12:30:00",
            }
        }
