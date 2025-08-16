"""
Data Transfer Objects for driver operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DriverCreateDTO(BaseModel):
    """DTO for creating a new driver."""

    nome_completo: str = Field(..., description="Nome completo do motorista")
    cnh: str = Field(..., description="Número da CNH")
    telefone: str = Field(..., description="Telefone de contato")
    email: Optional[str] = Field(None, description="Email do motorista")
    data_nascimento: Optional[datetime] = Field(
        None, description="Data de nascimento"
    )
    endereco: Optional[str] = Field(None, description="Endereço completo")
    status: str = Field("Ativo", description="Status do motorista")
    carro: Optional[str] = Field(
        None, description="Informações do carro utilizado"
    )
    observacoes: Optional[str] = Field(None, description="Observações")

    @field_validator("data_nascimento", mode="before")
    @classmethod
    def parse_data_nascimento(
        cls, value: Optional[str | datetime]
    ) -> Optional[datetime]:
        """Accept ISO (YYYY-MM-DD[THH:MM:SS]) or BR (DD/MM/YYYY) formats.

        Converts to a datetime at midnight when only a date is provided.
        """
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            v = value.strip()
            # Try full ISO datetime first
            try:
                # If only date part like YYYY-MM-DD
                if len(v) == 10 and v.count("-") == 2:
                    return datetime.fromisoformat(v + "T00:00:00")
                return datetime.fromisoformat(v)
            except Exception:
                pass
            # Try BR format DD/MM/YYYY
            try:
                return datetime.strptime(v, "%d/%m/%Y")
            except Exception:
                raise ValueError(
                    "Formato de data inválido. Use YYYY-MM-DD ou DD/MM/YYYY."
                )
        return None


class DriverResponseDTO(BaseModel):
    """DTO for driver response."""

    id: UUID
    nome_completo: str
    cnh: str
    telefone: str
    email: Optional[str]
    data_nascimento: Optional[datetime]
    endereco: Optional[str]
    status: str
    carro: Optional[str]
    observacoes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class DriverUpdateDTO(BaseModel):
    """DTO for updating driver."""

    nome_completo: Optional[str] = None
    cnh: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    endereco: Optional[str] = None
    status: Optional[str] = None
    carro: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator("data_nascimento", mode="before")
    @classmethod
    def parse_data_nascimento(
        cls, value: Optional[str | datetime]
    ) -> Optional[datetime]:
        """Accept ISO (YYYY-MM-DD[THH:MM:SS]) or BR (DD/MM/YYYY) formats for
        updates.
        """
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            v = value.strip()
            try:
                if len(v) == 10 and v.count("-") == 2:
                    return datetime.fromisoformat(v + "T00:00:00")
                return datetime.fromisoformat(v)
            except Exception:
                pass
            try:
                return datetime.strptime(v, "%d/%m/%Y")
            except Exception:
                raise ValueError(
                    "Formato de data inválido. Use YYYY-MM-DD ou DD/MM/YYYY."
                )
        return None


class DriverFilterDTO(BaseModel):
    """DTO for filtering drivers."""

    nome_completo: Optional[str] = None
    cnh: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    page: int = Field(1, ge=1, description="Página")
    page_size: int = Field(50, ge=1, le=100, description="Itens por página")


class PaginationDTO(BaseModel):
    """DTO for pagination information."""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class DriverListResponseDTO(BaseModel):
    """DTO for driver list response."""

    success: bool
    message: Optional[str] = None
    drivers: List[DriverResponseDTO]
    pagination: PaginationDTO


class DriverDeleteResponseDTO(BaseModel):
    """DTO for driver deletion response."""

    success: bool
    message: str


class DriverStatsDTO(BaseModel):
    """DTO for driver statistics."""

    success: bool
    message: Optional[str] = None
    stats: dict = {}


class DriverFilterOptionsDTO(BaseModel):
    """DTO for driver filter options."""

    success: bool
    message: Optional[str] = None
    statuses: List[str] = []


class DriverValidationErrorDTO(BaseModel):
    """DTO for driver validation errors."""

    success: bool = False
    message: str
    field: Optional[str] = None
    errors: List[str] = []


class ActiveDriverDTO(BaseModel):
    """DTO for active driver (simplified for dropdowns)."""

    id: UUID
    nome_completo: str
    cnh: str
    telefone: str


class ActiveDriverListResponseDTO(BaseModel):
    """DTO for active driver list response."""

    success: bool
    message: Optional[str] = None
    drivers: List[ActiveDriverDTO]
