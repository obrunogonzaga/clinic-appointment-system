"""Data transfer objects for tag operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


def _validate_hex_color(value: str) -> str:
    if not value:
        raise ValueError("Cor da tag é obrigatória")
    color = value.strip().lower()
    if not color.startswith("#") or len(color) != 7:
        raise ValueError("Cor inválida. Use o formato hexadecimal #RRGGBB.")
    hex_part = color[1:]
    if any(ch not in "0123456789abcdef" for ch in hex_part):
        raise ValueError("Cor inválida. Use o formato hexadecimal #RRGGBB.")
    return color


class TagCreateDTO(BaseModel):
    """Payload utilizado para criar uma nova tag."""

    name: str = Field(..., min_length=1, max_length=50, description="Nome da tag")
    color: str = Field(
        "#2563eb", description="Cor no formato hexadecimal #RRGGBB"
    )

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nome da tag é obrigatório")
        if len(cleaned) > 50:
            raise ValueError("Nome da tag deve ter no máximo 50 caracteres")
        return cleaned

    @field_validator("color")
    @classmethod
    def _check_color(cls, value: str) -> str:
        return _validate_hex_color(value)


class TagUpdateDTO(BaseModel):
    """Payload para atualização parcial de uma tag."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Novo nome da tag"
    )
    color: Optional[str] = Field(
        None, description="Nova cor no formato hexadecimal"
    )
    is_active: Optional[bool] = Field(
        None, description="Atualiza o status de ativação da tag"
    )

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nome da tag é obrigatório")
        if len(cleaned) > 50:
            raise ValueError("Nome da tag deve ter no máximo 50 caracteres")
        return cleaned

    @field_validator("color")
    @classmethod
    def _check_color(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return _validate_hex_color(value)


class TagResponseDTO(BaseModel):
    """Representação de uma tag retornada pela API."""

    id: UUID
    name: str
    color: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]


class TagSummaryDTO(BaseModel):
    """Resumo de tag utilizado em respostas de agendamento."""

    id: UUID
    name: str
    color: str


class TagListResponseDTO(BaseModel):
    """Resposta paginada com lista de tags."""

    success: bool
    message: Optional[str] = None
    tags: List[TagResponseDTO]
    page: int
    page_size: int
    total: int
