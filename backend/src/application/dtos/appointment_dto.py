"""Data Transfer Objects for appointment operations."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.dtos.tag_dto import TagSummaryDTO


class AppointmentScope(str, Enum):
    """Allowed temporal segments for appointment listings."""

    CURRENT = "current"
    HISTORY = "history"
    UNSCHEDULED = "unscheduled"


class AppointmentCreateDTO(BaseModel):
    """DTO for creating a new appointment."""

    nome_marca: str = Field(..., description="Nome da Marca")
    nome_unidade: str = Field(..., description="Nome da Unidade")
    nome_paciente: str = Field(..., description="Nome do Paciente")
    data_agendamento: Optional[datetime] = Field(
        None, description="Data do Agendamento"
    )
    hora_agendamento: Optional[str] = Field(
        None, description="Hora do Agendamento"
    )
    tipo_consulta: Optional[str] = Field(None, description="Tipo de Consulta")
    cip: Optional[str] = Field(
        None, description="Código CIP (Classificação Internacional de Procedimentos)"
    )
    status: str = Field("Pendente", description="Status do Agendamento")
    telefone: Optional[str] = Field(None, description="Telefone do Paciente")
    carro: Optional[str] = Field(
        None, description="Informações do carro utilizado"
    )
    car_id: Optional[str] = Field(None, description="ID do carro selecionado")
    logistics_package_id: Optional[str] = Field(
        None, description="ID do pacote logístico aplicado"
    )
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
    tags: List[str] = Field(
        default_factory=list,
        description="Lista de IDs de tags associadas ao agendamento",
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
    data_agendamento: Optional[datetime] = None
    hora_agendamento: Optional[str] = None
    tipo_consulta: Optional[str] = None
    cip: Optional[str] = None
    status: str
    telefone: Optional[str] = None
    carro: Optional[str] = None
    car_id: Optional[str] = None
    logistics_package_id: Optional[str] = None
    logistics_package_name: Optional[str] = None
    observacoes: Optional[str] = None
    driver_id: Optional[str] = None
    collector_id: Optional[str] = None
    # Campos de endereço
    cep: Optional[str] = Field(None, description="CEP do endereço de coleta")
    endereco_coleta: Optional[str] = Field(
        None, description="Endereço da coleta"
    )
    endereco_completo: Optional[str] = Field(
        None, description="Endereço completo não normalizado"
    )
    endereco_normalizado: Optional[Dict[str, Optional[str]]] = Field(
        None, description="Endereço normalizado em campos estruturados"
    )
    # Campos de documento do paciente
    documento_completo: Optional[str] = Field(
        None, description="Documento completo não normalizado da planilha"
    )
    documento_normalizado: Optional[Dict[str, Optional[str]]] = Field(
        None, description="Documentos normalizados (CPF e RG estruturados)"
    )
    cpf: Optional[str] = Field(
        None, description="CPF do paciente (apenas dígitos)"
    )
    rg: Optional[str] = Field(
        None, description="RG do paciente (apenas dígitos)"
    )
    # Campos de convênio
    numero_convenio: Optional[str] = None
    nome_convenio: Optional[str] = None
    carteira_convenio: Optional[str] = None
    cadastrado_por: Optional[str] = None
    agendado_por: Optional[str] = None
    canal_confirmacao: Optional[str] = None
    data_confirmacao: Optional[datetime] = None
    hora_confirmacao: Optional[str] = None
    tags: List[TagSummaryDTO] = Field(
        default_factory=list, description="Tags vinculadas ao agendamento"
    )
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
    scope: AppointmentScope = Field(
        default=AppointmentScope.CURRENT,
        description="Conjunto temporal (current|history)",
    )


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
    duplicates_found: int = 0
    errors: List[str] = []
    processing_time: Optional[float] = None
    past_appointments_blocked: int = 0
    past_appointments_examples: List[str] = []


class FilterOptionsDTO(BaseModel):
    """DTO for filter options."""

    success: bool
    message: Optional[str] = None
    units: List[str] = []
    brands: List[str] = []
    statuses: List[str] = []
    max_tags_per_appointment: int = Field(
        5, description="Limite máximo de tags permitido por agendamento"
    )


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
    cip: Optional[str] = None
    status: Optional[str] = None
    telefone: Optional[str] = None
    carro: Optional[str] = None
    observacoes: Optional[str] = None
    driver_id: Optional[str] = None
    collector_id: Optional[str] = None
    car_id: Optional[str] = None
    logistics_package_id: Optional[str] = None
    # Campos de convênio
    numero_convenio: Optional[str] = None
    nome_convenio: Optional[str] = None
    carteira_convenio: Optional[str] = None
    canal_confirmacao: Optional[str] = None
    data_confirmacao: Optional[datetime] = None
    hora_confirmacao: Optional[str] = None
    cep: Optional[str] = None
    endereco_normalizado: Optional[Dict[str, Optional[str]]] = None
    documento_normalizado: Optional[Dict[str, Optional[str]]] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    # Tags vinculadas (IDs)
    tags: Optional[List[str]] = None


class AppointmentDeleteResponseDTO(BaseModel):
    """DTO for appointment deletion response."""

    success: bool
    message: str
