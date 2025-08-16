"""
Data Transfer Objects for collector operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CollectorCreateDTO(BaseModel):
    """DTO for creating a new collector."""

    nome_completo: str = Field(..., description="Nome completo da coletora")
    cpf: str = Field(..., description="Número do CPF")
    telefone: str = Field(..., description="Telefone de contato")
    email: Optional[str] = Field(None, description="Email da coletora")
    data_nascimento: Optional[datetime] = Field(
        None, description="Data de nascimento"
    )
    endereco: Optional[str] = Field(None, description="Endereço completo")
    status: str = Field("Ativo", description="Status da coletora")
    carro: Optional[str] = Field(
        None, description="Informações do carro utilizado"
    )
    observacoes: Optional[str] = Field(None, description="Observações")
    registro_profissional: Optional[str] = Field(
        None, description="Registro profissional"
    )
    especializacao: Optional[str] = Field(None, description="Especialização")

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


class CollectorResponseDTO(BaseModel):
    """DTO for collector response."""

    id: UUID
    nome_completo: str
    cpf: str
    telefone: str
    email: Optional[str]
    data_nascimento: Optional[datetime]
    endereco: Optional[str]
    status: str
    carro: Optional[str]
    observacoes: Optional[str]
    registro_profissional: Optional[str]
    especializacao: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class CollectorUpdateDTO(BaseModel):
    """DTO for updating collector."""

    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    data_nascimento: Optional[datetime] = None
    endereco: Optional[str] = None
    status: Optional[str] = None
    carro: Optional[str] = None
    observacoes: Optional[str] = None
    registro_profissional: Optional[str] = None
    especializacao: Optional[str] = None

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


class CollectorFilterDTO(BaseModel):
    """DTO for filtering collectors."""

    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
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


class CollectorListResponseDTO(BaseModel):
    """DTO for collector list response."""

    success: bool
    message: Optional[str] = None
    collectors: List[CollectorResponseDTO]
    pagination: PaginationDTO


class CollectorDeleteResponseDTO(BaseModel):
    """DTO for collector deletion response."""

    success: bool
    message: str


class CollectorStatsDTO(BaseModel):
    """DTO for collector statistics."""

    success: bool
    message: Optional[str] = None
    stats: dict = {}


class CollectorFilterOptionsDTO(BaseModel):
    """DTO for collector filter options."""

    success: bool
    message: Optional[str] = None
    statuses: List[str] = []


class CollectorValidationErrorDTO(BaseModel):
    """DTO for collector validation errors."""

    success: bool = False
    message: str
    field: Optional[str] = None
    errors: List[str] = []


class ActiveCollectorDTO(BaseModel):
    """DTO for active collector (simplified for dropdowns)."""

    id: UUID
    nome_completo: str
    cpf: str
    telefone: str


class ActiveCollectorListResponseDTO(BaseModel):
    """DTO for active collector list response."""

    success: bool
    message: Optional[str] = None
    collectors: List[ActiveCollectorDTO]
