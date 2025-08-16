"""
Data Transfer Objects for appointment operations.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AppointmentCreateDTO(BaseModel):
    """DTO for creating a new appointment."""

    nome_marca: str = Field(..., description="Nome da Marca")
    nome_unidade: str = Field(..., description="Nome da Unidade")
    nome_paciente: str = Field(..., description="Nome do Paciente")
    data_agendamento: datetime = Field(..., description="Data do Agendamento")
    hora_agendamento: str = Field(..., description="Hora do Agendamento")
    tipo_consulta: Optional[str] = Field(None, description="Tipo de Consulta")
    status: str = Field("Confirmado", description="Status do Agendamento")
    telefone: Optional[str] = Field(None, description="Telefone do Paciente")
    observacoes: Optional[str] = Field(None, description="Observações")
    driver_id: Optional[str] = Field(None, description="ID do Motorista")
    collector_id: Optional[str] = Field(None, description="ID da Coletora")
    # Campos de convênio
    numero_convenio: Optional[str] = Field(
        None, description="Número do convênio"
    )
    nome_convenio: Optional[str] = Field(None, description="Nome do convênio")
    carteira_convenio: Optional[str] = Field(
        None, description="Número da carteira do convênio"
    )


class AppointmentUpdateDTO(BaseModel):
    """DTO for updating an appointment."""

    driver_id: Optional[str] = Field(None, description="ID do Motorista")
    collector_id: Optional[str] = Field(None, description="ID da Coletora")


class AppointmentResponseDTO(BaseModel):
    """DTO for appointment response."""

    id: UUID
    nome_marca: str
    nome_unidade: str
    nome_paciente: str
    data_agendamento: datetime
    hora_agendamento: str
    tipo_consulta: Optional[str]
    status: str
    telefone: Optional[str]
    observacoes: Optional[str]
    driver_id: Optional[str]
    collector_id: Optional[str]
    # Campos de convênio
    numero_convenio: Optional[str]
    nome_convenio: Optional[str]
    carteira_convenio: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class AppointmentFilterDTO(BaseModel):
    """DTO for filtering appointments."""

    nome_unidade: Optional[str] = None
    nome_marca: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
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


class AppointmentListResponseDTO(BaseModel):
    """DTO for appointment list response."""

    success: bool
    message: Optional[str] = None
    appointments: List[AppointmentResponseDTO]
    pagination: PaginationDTO


class ExcelUploadResponseDTO(BaseModel):
    """DTO for Excel upload response."""

    success: bool
    message: str
    filename: Optional[str] = None
    total_rows: int
    valid_rows: int
    invalid_rows: int
    imported_appointments: int
    errors: List[str] = []
    processing_time: Optional[float] = None


class FilterOptionsDTO(BaseModel):
    """DTO for filter options."""

    success: bool
    message: Optional[str] = None
    units: List[str] = []
    brands: List[str] = []
    statuses: List[str] = []


class DashboardStatsDTO(BaseModel):
    """DTO for dashboard statistics."""

    success: bool
    message: Optional[str] = None
    stats: Dict = {}


class AppointmentFullUpdateDTO(BaseModel):
    """DTO for full appointment update with all fields."""

    nome_marca: Optional[str] = None
    nome_unidade: Optional[str] = None
    nome_paciente: Optional[str] = None
    data_agendamento: Optional[datetime] = None
    hora_agendamento: Optional[str] = None
    tipo_consulta: Optional[str] = None
    status: Optional[str] = None
    telefone: Optional[str] = None
    observacoes: Optional[str] = None
    driver_id: Optional[str] = None
    collector_id: Optional[str] = None
    # Campos de convênio
    numero_convenio: Optional[str] = None
    nome_convenio: Optional[str] = None
    carteira_convenio: Optional[str] = None


class AppointmentDeleteResponseDTO(BaseModel):
    """DTO for appointment deletion response."""

    success: bool
    message: str
