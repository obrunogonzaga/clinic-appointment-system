"""
Data Transfer Objects for car operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CarCreateDTO(BaseModel):
    """DTO for creating a new car."""

    nome: str = Field(..., description="Nome identificador do carro")
    unidade: str = Field(..., description="Unidade associada ao carro")
    placa: Optional[str] = Field(None, description="Placa do veículo")
    modelo: Optional[str] = Field(None, description="Modelo do veículo")
    cor: Optional[str] = Field(None, description="Cor do veículo")
    status: str = Field("Ativo", description="Status do carro")
    observacoes: Optional[str] = Field(None, description="Observações")


class CarResponseDTO(BaseModel):
    """DTO for car response."""

    id: UUID
    nome: str
    unidade: str
    placa: Optional[str]
    modelo: Optional[str]
    cor: Optional[str]
    status: str
    observacoes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class CarUpdateDTO(BaseModel):
    """DTO for updating car."""

    nome: Optional[str] = None
    unidade: Optional[str] = None
    placa: Optional[str] = None
    modelo: Optional[str] = None
    cor: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None


class CarFilterDTO(BaseModel):
    """DTO for filtering cars."""

    nome: Optional[str] = None
    unidade: Optional[str] = None
    placa: Optional[str] = None
    modelo: Optional[str] = None
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


class CarListResponseDTO(BaseModel):
    """DTO for car list response."""

    success: bool
    message: Optional[str] = None
    cars: List[CarResponseDTO]
    pagination: PaginationDTO


class CarDeleteResponseDTO(BaseModel):
    """DTO for car deletion response."""

    success: bool
    message: str


class CarStatsDTO(BaseModel):
    """DTO for car statistics."""

    success: bool
    message: Optional[str] = None
    stats: dict = {}


class CarFilterOptionsDTO(BaseModel):
    """DTO for car filter options."""

    success: bool
    message: Optional[str] = None
    statuses: List[str] = []
    unidades: List[str] = []


class CarValidationErrorDTO(BaseModel):
    """DTO for car validation errors."""

    success: bool = False
    message: str
    field: Optional[str] = None
    errors: List[str] = []


class ActiveCarDTO(BaseModel):
    """DTO for active car (simplified for dropdowns)."""

    id: UUID
    nome: str
    unidade: str
    placa: Optional[str]


class ActiveCarListResponseDTO(BaseModel):
    """DTO for active car list response."""

    success: bool
    message: Optional[str] = None
    cars: List[ActiveCarDTO]


class CarFromStringDTO(BaseModel):
    """DTO for creating car from string (like from Excel import)."""

    car_string: str = Field(..., description="String do carro (ex: 'CENTER 3 CARRO 1 - UND84')")


class CarFromStringResponseDTO(BaseModel):
    """DTO for car from string response."""

    success: bool
    message: Optional[str] = None
    car: Optional[CarResponseDTO] = None
    created: bool = False  # True if car was created, False if already existed