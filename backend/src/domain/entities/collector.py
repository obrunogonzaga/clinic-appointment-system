"""
Collector entity representing a medical sample collector.
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator
from src.domain.base import Entity


class Collector(Entity):
    """
    Collector entity representing a medical sample collector.

    This entity contains all essential information about a collector
    responsible for collecting medical samples from patients.
    """

    # Required fields
    nome_completo: str = Field(..., description="Nome completo da coletora")
    cpf: str = Field(
        ..., description="Número do CPF (Cadastro de Pessoa Física)"
    )
    telefone: str = Field(..., description="Telefone de contato da coletora")

    # Optional fields
    email: Optional[str] = Field(None, description="Email da coletora")
    data_nascimento: Optional[datetime] = Field(
        None, description="Data de nascimento"
    )
    endereco: Optional[str] = Field(None, description="Endereço completo")
    status: Optional[str] = Field("Ativo", description="Status da coletora")
    observacoes: Optional[str] = Field(
        None, description="Observações adicionais"
    )
    registro_profissional: Optional[str] = Field(
        None, description="Registro profissional (CRF, COREN, etc.)"
    )
    especializacao: Optional[str] = Field(
        None, description="Especialização ou área de atuação"
    )

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
            raise ValueError(
                "Nome completo deve ter pelo menos nome e sobrenome"
            )

        return value.strip()

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        """Validate CPF format (Brazilian tax ID)."""
        if not value or not value.strip():
            raise ValueError("CPF é obrigatório")

        # Remove spaces and special characters
        cpf = re.sub(r"\D", "", value.strip())

        # CPF must have exactly 11 digits
        if len(cpf) != 11:
            raise ValueError("CPF deve ter exatamente 11 dígitos")

        # Check for invalid CPFs (all same digits)
        if cpf == cpf[0] * 11:
            raise ValueError("CPF inválido")

        # Validate CPF algorithm
        if not cls._validate_cpf_algorithm(cpf):
            raise ValueError("CPF inválido")

        return cpf

    @classmethod
    def _validate_cpf_algorithm(cls, cpf: str) -> bool:
        """Validate CPF using the official algorithm."""
        if len(cpf) != 11:
            return False

        # Convert to list of integers
        digits = [int(d) for d in cpf]

        # First verification digit
        sum1 = sum(digits[i] * (10 - i) for i in range(9))
        remainder1 = sum1 % 11
        first_digit = 0 if remainder1 < 2 else 11 - remainder1

        if digits[9] != first_digit:
            return False

        # Second verification digit
        sum2 = sum(digits[i] * (11 - i) for i in range(10))
        remainder2 = sum2 % 11
        second_digit = 0 if remainder2 < 2 else 11 - remainder2

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
        """Validate collector status."""
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
                "id": "507f1f77bcf86cd799439012",
                "nome_completo": "Maria Silva Santos",
                "cpf": "12345678901",
                "telefone": "11999887766",
                "email": "maria.silva@email.com",
                "data_nascimento": "1990-05-20T00:00:00",
                "endereco": "Rua das Flores, 456 - São Paulo, SP",
                "status": "Ativo",
                "observacoes": "Coletora experiente, especializada em coletas domiciliares",
                "registro_profissional": "COREN-SP 123456",
                "especializacao": "Coleta domiciliar",
                "created_at": "2025-01-14T10:00:00",
                "updated_at": "2025-01-14T10:00:00",
            }
        }
