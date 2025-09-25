"""Domain entity representing a reusable logistics package."""

from typing import Optional

from pydantic import Field, field_validator

from src.domain.base import Entity


class LogisticsPackage(Entity):
    """Aggregate of car, driver and collector to speed up assignments."""

    nome: str = Field(..., description="Nome descritivo do pacote logístico")
    descricao: Optional[str] = Field(
        None, description="Notas adicionais para identificar o pacote"
    )
    driver_id: str = Field(..., description="Identificador do motorista")
    driver_nome: str = Field(..., description="Nome do motorista no momento do cadastro")
    collector_id: str = Field(..., description="Identificador da coletora")
    collector_nome: str = Field(
        ..., description="Nome da coletora no momento do cadastro"
    )
    car_id: str = Field(..., description="Identificador do carro associado")
    car_nome: str = Field(..., description="Nome ou apelido do carro")
    car_unidade: Optional[str] = Field(
        None, description="Unidade associada ao carro, quando disponível"
    )
    car_display_name: str = Field(
        ..., description="Rótulo pronto para preencher o campo `carro` do agendamento"
    )
    status: str = Field(
        "Ativo",
        description="Status operacional do pacote",
    )

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Nome do pacote é obrigatório")
        return value.strip()

    @field_validator(
        "driver_id",
        "driver_nome",
        "collector_id",
        "collector_nome",
        "car_id",
        "car_nome",
        "car_display_name",
    )
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Campo obrigatório não pode estar vazio")
        return value.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> str:
        allowed = {"Ativo", "Inativo"}
        if value is None:
            return "Ativo"
        normalized = value.strip().title()
        if normalized not in allowed:
            raise ValueError(
                "Status inválido. Utilize 'Ativo' ou 'Inativo' para pacotes logísticos."
            )
        return normalized

