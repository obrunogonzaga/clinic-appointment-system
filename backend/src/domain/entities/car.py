"""
Car entity representing a vehicle used for patient transport.
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator

from src.domain.base import Entity


class Car(Entity):
    """
    Car entity representing a vehicle used for patient transport and collection.

    This entity contains all essential information about vehicles
    used in the healthcare logistics operations.
    """

    # Required fields
    nome: str = Field(..., description="Nome identificador do carro")
    unidade: str = Field(..., description="Unidade associada ao carro")

    # Optional fields
    placa: Optional[str] = Field(None, description="Placa do veículo")
    modelo: Optional[str] = Field(None, description="Modelo do veículo")
    cor: Optional[str] = Field(None, description="Cor do veículo")
    status: Optional[str] = Field("Ativo", description="Status do carro")
    observacoes: Optional[str] = Field(
        None, description="Observações adicionais"
    )

    # Metadata fields (handled by Entity base class)
    # created_at: datetime
    # updated_at: datetime

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, value: str) -> str:
        """Validate that name is not empty."""
        if not value or not value.strip():
            raise ValueError("Nome do carro é obrigatório")
        return value.strip()

    @field_validator("unidade")
    @classmethod
    def validate_unidade(cls, value: str) -> str:
        """Validate that unidade is not empty."""
        if not value or not value.strip():
            raise ValueError("Unidade é obrigatória")
        return value.strip()

    @field_validator("placa")
    @classmethod
    def validate_placa(cls, value: Optional[str]) -> Optional[str]:
        """Validate Brazilian license plate format."""
        if not value:
            return None

        placa = value.strip().upper()
        if not placa:
            return None

        # Remove spaces and hyphens
        placa = placa.replace(" ", "").replace("-", "")

        # Brazilian license plate patterns:
        # Old format: ABC1234 (3 letters + 4 numbers)
        # Mercosul format: ABC1D23 (3 letters + 1 number + 1 letter + 2 numbers)
        old_pattern = r"^[A-Z]{3}\d{4}$"
        mercosul_pattern = r"^[A-Z]{3}\d[A-Z]\d{2}$"

        if not (
            re.match(old_pattern, placa) or re.match(mercosul_pattern, placa)
        ):
            raise ValueError(
                "Placa deve estar no formato brasileiro (ABC1234 ou ABC1D23)"
            )

        return placa

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> str:
        """Validate car status."""
        if not value:
            return "Ativo"

        valid_statuses = ["Ativo", "Inativo", "Manutenção", "Vendido"]

        if value not in valid_statuses:
            raise ValueError(
                f"Status inválido. Valores permitidos: {', '.join(valid_statuses)}"
            )

        return value

    @classmethod
    def extract_car_info_from_string(cls, car_string: str) -> tuple[str, str]:
        """
        Extract car name and unit from appointment car field.

        Args:
            car_string: String like "CENTER 3 CARRO 1 - UND84"

        Returns:
            tuple: (car_name, unit) like ("CENTER 3 CARRO 1", "UND84")
        """
        if not car_string or not car_string.strip():
            raise ValueError("String do carro não pode estar vazia")

        # Pattern to match "CENTER X CARRO Y - UNDZ" format
        pattern = r"^(.+?)\s*-\s*([A-Z0-9]+)$"
        match = re.match(pattern, car_string.strip())

        if not match:
            # If no unit pattern found, treat entire string as car name
            # and extract unit from context or use default
            return car_string.strip(), "UND"

        car_name = match.group(1).strip()
        unit = match.group(2).strip()

        return car_name, unit

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "nome": "CENTER 3 CARRO 1",
                "unidade": "UND84",
                "placa": "ABC1234",
                "modelo": "Honda Civic",
                "cor": "Prata",
                "status": "Ativo",
                "observacoes": "Veículo em excelente estado",
                "created_at": "2025-01-14T10:00:00",
                "updated_at": "2025-01-14T10:00:00",
            }
        }
