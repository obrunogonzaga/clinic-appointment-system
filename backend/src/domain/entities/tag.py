"""Tag entity and related value objects."""

from typing import Optional

from pydantic import Field, field_validator

from src.domain.base import Entity, ValueObject


HEX_COLOR_ERROR = (
    "Cor inválida. Use o formato hexadecimal #RRGGBB."
)


class Tag(Entity):
    """Domain entity representing a tag that can be attached to appointments."""

    name: str = Field(..., min_length=1, max_length=50, description="Nome da tag")
    color: str = Field(
        "#2563eb",
        description="Cor no formato hexadecimal",
    )
    is_active: bool = Field(
        True,
        description="Indica se a tag está ativa para seleção",
    )

    @field_validator("name", mode="before")
    @classmethod
    def _strip_name(cls, value: Optional[str]) -> str:
        """Ensure tag name is present and trimmed."""
        if not value or not isinstance(value, str):
            raise ValueError("Nome da tag é obrigatório")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nome da tag é obrigatório")
        if len(cleaned) > 50:
            raise ValueError("Nome da tag deve ter no máximo 50 caracteres")
        return cleaned

    @field_validator("color", mode="before")
    @classmethod
    def _normalize_color(cls, value: Optional[str]) -> str:
        """Normalize and validate hexadecimal color representation."""
        if value is None:
            return "#2563eb"
        if not isinstance(value, str):
            raise ValueError(HEX_COLOR_ERROR)
        color = value.strip().lower()
        if not color.startswith("#"):
            raise ValueError(HEX_COLOR_ERROR)
        if len(color) != 7:
            raise ValueError(HEX_COLOR_ERROR)
        hex_part = color[1:]
        if any(ch not in "0123456789abcdef" for ch in hex_part):
            raise ValueError(HEX_COLOR_ERROR)
        return color

    def normalized_name(self) -> str:
        """Return normalized representation used for uniqueness checks."""
        return self.name.lower()


class TagReference(ValueObject):
    """Value object storing lightweight tag information for appointments."""

    id: str = Field(..., description="Identificador da tag")
    name: str = Field(..., description="Nome da tag")
    color: str = Field(..., description="Cor no formato hexadecimal")

    @field_validator("name", mode="before")
    @classmethod
    def _strip_name(cls, value: Optional[str]) -> str:
        if value is None:
            raise ValueError("Nome da tag é obrigatório")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nome da tag é obrigatório")
        return cleaned

    @field_validator("color", mode="before")
    @classmethod
    def _normalize_color(cls, value: Optional[str]) -> str:
        if value is None:
            raise ValueError(HEX_COLOR_ERROR)
        color = value.strip().lower()
        if not color.startswith("#") or len(color) != 7:
            raise ValueError(HEX_COLOR_ERROR)
        hex_part = color[1:]
        if any(ch not in "0123456789abcdef" for ch in hex_part):
            raise ValueError(HEX_COLOR_ERROR)
        return color
