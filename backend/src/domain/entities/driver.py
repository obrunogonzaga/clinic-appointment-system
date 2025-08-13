"""
Driver entity representing a delivery/transport driver.
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator
from src.domain.base import Entity


class Driver(Entity):
    """
    Driver entity representing a delivery/transport driver.

    This entity contains all essential information about a driver
    responsible for patient transport and home collections.
    """

    # Required fields
    nome_completo: str = Field(..., description="Nome completo do motorista")
    cnh: str = Field(
        ..., description="Número da CNH (Carteira Nacional de Habilitação)"
    )
    telefone: str = Field(..., description="Telefone de contato do motorista")

    # Optional fields
    email: Optional[str] = Field(None, description="Email do motorista")
    data_nascimento: Optional[datetime] = Field(None, description="Data de nascimento")
    endereco: Optional[str] = Field(None, description="Endereço completo")
    status: Optional[str] = Field("Ativo", description="Status do motorista")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")

    # Metadata fields (handled by Entity base class)
    # created_at: datetime
    # updated_at: datetime

    @field_validator("nome_completo")
    @classmethod
    def validate_nome_completo(cls, value: str) -> str:
        """Validate that name is not empty and has at least 2 words."""
        if not value or not value.strip():
            raise ValueError("Nome completo é obrigatório")

        name_parts = value.strip().split()
        if len(name_parts) < 2:
            raise ValueError("Nome completo deve ter pelo menos nome e sobrenome")

        return value.strip()

    @field_validator("cnh")
    @classmethod
    def validate_cnh(cls, value: str) -> str:
        """Validate CNH format (Brazilian driver's license)."""
        if not value or not value.strip():
            raise ValueError("CNH é obrigatória")

        # Remove spaces and special characters
        cnh = re.sub(r"\D", "", value.strip())

        # CNH must have exactly 11 digits
        if len(cnh) != 11:
            raise ValueError("CNH deve ter exatamente 11 dígitos")

        # Basic validation algorithm for CNH
        if not cls._validate_cnh_algorithm(cnh):
            raise ValueError("CNH inválida")

        return cnh

    @classmethod
    def _validate_cnh_algorithm(cls, cnh: str) -> bool:
        """Validate CNH using the official algorithm."""
        if len(cnh) != 11:
            return False

        # Convert to list of integers
        digits = [int(d) for d in cnh]

        # First verification digit
        sum1 = sum(digits[i] * (9 - i) for i in range(9))
        remainder1 = sum1 % 11
        first_digit = 0 if remainder1 < 2 else 11 - remainder1

        if digits[9] != first_digit:
            return False

        # Second verification digit
        # Keep same calculation as frontend (JS) to avoid modulo
        # differences between Python and JavaScript for negatives.
        sum2 = sum(digits[i] * (1 - i) for i in range(10))
        # Emulate JS remainder: r = a - trunc(a/11) * 11
        remainder2_js = sum2 - int(sum2 / 11) * 11
        second_digit = 0 if remainder2_js < 2 else 11 - remainder2_js

        return digits[10] == second_digit

    @field_validator("telefone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Validate and normalize phone number."""
        if not value or not value.strip():
            raise ValueError("Telefone é obrigatório")

        # Remove common formatting characters
        phone = (
            value.strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        # Brazilian phone validation
        if not (10 <= len(phone) <= 11):
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")

        # Must start with valid area code (11-99)
        if len(phone) >= 2:
            area_code = int(phone[:2])
            if not (11 <= area_code <= 99):
                raise ValueError("Código de área inválido")

        return phone

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        """Validate email format."""
        if not value:
            return None

        email = value.strip()
        if not email:
            return None

        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValueError("Email inválido")

        return email

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> str:
        """Validate driver status."""
        if not value:
            return "Ativo"

        valid_statuses = ["Ativo", "Inativo", "Suspenso", "Férias"]

        if value not in valid_statuses:
            raise ValueError(
                f"Status inválido. Valores permitidos: {', '.join(valid_statuses)}"
            )

        return value

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "nome_completo": "João Silva Santos",
                "cnh": "12345678901",
                "telefone": "11999887766",
                "email": "joao.silva@email.com",
                "data_nascimento": "1985-03-15T00:00:00",
                "endereco": "Rua das Flores, 123 - São Paulo, SP",
                "status": "Ativo",
                "observacoes": "Motorista experiente, conhece bem a região",
                "created_at": "2025-01-14T10:00:00",
                "updated_at": "2025-01-14T10:00:00",
            }
        }
