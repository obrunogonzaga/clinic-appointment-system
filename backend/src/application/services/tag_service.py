"""Serviço contendo regras de negócio para gestão de tags."""

from typing import Dict, Optional

from src.application.dtos.tag_dto import (
    TagCreateDTO,
    TagListResponseDTO,
    TagResponseDTO,
    TagSummaryDTO,
    TagUpdateDTO,
)
from src.domain.entities.tag import Tag
from src.domain.repositories.appointment_repository_interface import (
    AppointmentRepositoryInterface,
)
from src.domain.repositories.tag_repository_interface import (
    TagRepositoryInterface,
)


class TagService:
    """Coordenador das operações de CRUD de tags com validações de domínio."""

    def __init__(
        self,
        tag_repository: TagRepositoryInterface,
        appointment_repository: AppointmentRepositoryInterface,
    ) -> None:
        self.tag_repository = tag_repository
        self.appointment_repository = appointment_repository

    @staticmethod
    def _normalize_name(name: str) -> str:
        return name.strip().lower()

    async def create_tag(self, payload: TagCreateDTO) -> Dict[str, object]:
        normalized_name = self._normalize_name(payload.name)

        if await self.tag_repository.exists_by_normalized_name(normalized_name):
            return {
                "success": False,
                "message": "Já existe uma tag com este nome.",
                "error_code": "conflict",
            }

        tag = Tag(name=payload.name, color=payload.color)
        await self.tag_repository.create(tag)

        return {
            "success": True,
            "message": "Tag criada com sucesso.",
            "tag": TagResponseDTO(**tag.model_dump()),
        }

    async def list_tags(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        include_inactive: bool = True,
    ) -> Dict[str, object]:
        page = max(page, 1)
        page_size = max(min(page_size, 100), 1)
        skip = (page - 1) * page_size

        tags, total = await self.tag_repository.list(
            search=search,
            skip=skip,
            limit=page_size,
            include_inactive=include_inactive,
        )

        dto = TagListResponseDTO(
            success=True,
            tags=[TagResponseDTO(**tag.model_dump()) for tag in tags],
            page=page,
            page_size=page_size,
            total=total,
        )

        return dto.model_dump()

    async def update_tag(
        self, tag_id: str, payload: TagUpdateDTO
    ) -> Dict[str, object]:
        update_data = payload.model_dump(exclude_none=True)
        if not update_data:
            return {
                "success": False,
                "message": "Nenhuma alteração fornecida.",
                "error_code": "no_changes",
            }

        current_tag = await self.tag_repository.find_by_id(tag_id)
        if not current_tag:
            return {
                "success": False,
                "message": "Tag não encontrada.",
                "error_code": "not_found",
            }

        if "name" in update_data:
            normalized_name = self._normalize_name(update_data["name"])
            current_normalized = self._normalize_name(current_tag.name)
            if normalized_name != current_normalized:
                exists = await self.tag_repository.exists_by_normalized_name(
                    normalized_name, exclude_id=tag_id
                )
                if exists:
                    return {
                        "success": False,
                        "message": "Já existe uma tag com este nome.",
                        "error_code": "conflict",
                    }
            else:
                update_data.pop("name")

        if (
            "color" in update_data
            and update_data["color"].strip().lower() == current_tag.color
        ):
            update_data.pop("color")

        if (
            "is_active" in update_data
            and update_data["is_active"] == current_tag.is_active
        ):
            update_data.pop("is_active")

        if not update_data:
            return {
                "success": False,
                "message": "Nenhuma alteração fornecida.",
                "error_code": "no_changes",
            }

        updated = await self.tag_repository.update(tag_id, update_data)
        if not updated:
            return {
                "success": False,
                "message": "Tag não encontrada.",
                "error_code": "not_found",
            }

        if (
            updated.name != current_tag.name
            or updated.color != current_tag.color
        ):
            await self.appointment_repository.update_tag_references(
                tag_id=str(updated.id),
                name=updated.name,
                color=updated.color,
            )

        return {
            "success": True,
            "message": "Tag atualizada com sucesso.",
            "tag": TagResponseDTO(**updated.model_dump()),
        }

    async def delete_tag(self, tag_id: str) -> Dict[str, object]:
        tag = await self.tag_repository.find_by_id(tag_id)
        if not tag:
            return {
                "success": False,
                "message": "Tag não encontrada.",
                "error_code": "not_found",
            }

        usage_count = await self.appointment_repository.count_by_tag(tag_id)
        if usage_count > 0:
            return {
                "success": False,
                "message": "Tag não pode ser removida porque está associada a agendamentos.",
                "error_code": "in_use",
                "usage_count": usage_count,
            }

        deleted = await self.tag_repository.delete(tag_id)
        if not deleted:
            return {
                "success": False,
                "message": "Não foi possível remover a tag.",
                "error_code": "unknown",
            }

        return {
            "success": True,
            "message": "Tag removida com sucesso.",
        }

    async def get_tag_summary(self, tag_id: str) -> Optional[TagSummaryDTO]:
        tag = await self.tag_repository.find_by_id(tag_id)
        if not tag:
            return None
        return TagSummaryDTO(
            **tag.model_dump(include={"id", "name", "color"})
        )

    async def fetch_active_tags_by_ids(
        self, tag_ids: list[str]
    ) -> Dict[str, TagSummaryDTO]:
        """Utility used por outros serviços para mapear tags."""
        if not tag_ids:
            return {}
        raw_tags = await self.tag_repository.find_by_ids(tag_ids)
        summaries = {
            str(tag.id): TagSummaryDTO(
                **tag.model_dump(include={"id", "name", "color"})
            )
            for tag in raw_tags
            if tag.is_active
        }
        return summaries
