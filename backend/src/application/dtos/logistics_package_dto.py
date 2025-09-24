"""DTOs for logistics package operations."""

from typing import Optional

from pydantic import BaseModel, Field


class LogisticsPackageCreateDTO(BaseModel):
    nome: str = Field(..., description="Nome do pacote logístico")
    descricao: Optional[str] = Field(
        None, description="Informações adicionais sobre o pacote"
    )
    driver_id: str = Field(..., description="Identificador do motorista")
    collector_id: str = Field(..., description="Identificador da coletora")
    car_id: str = Field(..., description="Identificador do carro")


class LogisticsPackageUpdateDTO(BaseModel):
    nome: Optional[str] = Field(None, description="Nome do pacote")
    descricao: Optional[str] = Field(None, description="Notas adicionais")
    driver_id: Optional[str] = Field(None, description="Motorista associado")
    collector_id: Optional[str] = Field(None, description="Coletora associada")
    car_id: Optional[str] = Field(None, description="Carro associado")
    status: Optional[str] = Field(None, description="Status do pacote")


class LogisticsPackageResponseDTO(BaseModel):
    id: str
    nome: str
    descricao: Optional[str]
    driver_id: str
    driver_nome: str
    collector_id: str
    collector_nome: str
    car_id: str
    car_nome: str
    car_unidade: Optional[str]
    car_display_name: str
    status: str

