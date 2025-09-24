"""Tests for the TagService business logic."""

from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.dtos.tag_dto import TagCreateDTO, TagUpdateDTO
from src.application.services.tag_service import TagService
from src.domain.entities.tag import Tag


@pytest.mark.asyncio
async def test_create_tag_success() -> None:
    tag_repository = MagicMock()
    tag_repository.exists_by_normalized_name = AsyncMock(return_value=False)
    tag_repository.create = AsyncMock()

    appointment_repository = MagicMock()

    service = TagService(tag_repository, appointment_repository)

    payload = TagCreateDTO(name="Urgente", color="#ff0000")
    result = await service.create_tag(payload)

    assert result["success"] is True
    assert result["tag"].name == "Urgente"
    tag_repository.create.assert_awaited()


@pytest.mark.asyncio
async def test_create_tag_conflict() -> None:
    tag_repository = MagicMock()
    tag_repository.exists_by_normalized_name = AsyncMock(return_value=True)

    service = TagService(tag_repository, MagicMock())

    payload = TagCreateDTO(name="Urgente", color="#ff0000")
    result = await service.create_tag(payload)

    assert result["success"] is False
    assert result["error_code"] == "conflict"
    tag_repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_list_tags_returns_paginated_result() -> None:
    tag_repository = MagicMock()
    tag_repository.list = AsyncMock(
        return_value=(
            [Tag(id=uuid4(), name="Urgente", color="#ff0000")],
            1,
        )
    )

    service = TagService(tag_repository, MagicMock())

    result = await service.list_tags(page=1, page_size=10)

    assert result["success"] is True
    assert result["total"] == 1
    assert len(result["tags"]) == 1
    assert result["tags"][0]["name"] == "Urgente"


@pytest.mark.asyncio
async def test_update_tag_propagates_changes() -> None:
    tag_id = str(uuid4())
    existing = Tag(id=uuid4(), name="Urgente", color="#ff0000")
    updated = Tag(id=existing.id, name="Prioridade", color="#00ff00")

    tag_repository = MagicMock()
    tag_repository.find_by_id = AsyncMock(return_value=existing)
    tag_repository.exists_by_normalized_name = AsyncMock(return_value=False)
    tag_repository.update = AsyncMock(return_value=updated)

    appointment_repository = MagicMock()
    appointment_repository.update_tag_references = AsyncMock(return_value=1)

    service = TagService(tag_repository, appointment_repository)

    payload = TagUpdateDTO(name="Prioridade", color="#00ff00")
    result = await service.update_tag(tag_id, payload)

    assert result["success"] is True
    appointment_repository.update_tag_references.assert_awaited_once_with(
        tag_id=str(updated.id), name="Prioridade", color="#00ff00"
    )


@pytest.mark.asyncio
async def test_update_tag_conflict_returns_error() -> None:
    tag_id = str(uuid4())
    existing = Tag(id=uuid4(), name="Urgente", color="#ff0000")

    tag_repository = MagicMock()
    tag_repository.find_by_id = AsyncMock(return_value=existing)
    tag_repository.exists_by_normalized_name = AsyncMock(return_value=True)

    service = TagService(tag_repository, MagicMock())

    payload = TagUpdateDTO(name="Prioridade")
    result = await service.update_tag(tag_id, payload)

    assert result["success"] is False
    assert result["error_code"] == "conflict"
    tag_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_tag_no_changes_returns_error() -> None:
    tag_id = str(uuid4())
    existing = Tag(id=uuid4(), name="Urgente", color="#ff0000", is_active=True)

    tag_repository = MagicMock()
    tag_repository.find_by_id = AsyncMock(return_value=existing)
    tag_repository.exists_by_normalized_name = AsyncMock()

    service = TagService(tag_repository, MagicMock())

    payload = TagUpdateDTO(name="Urgente", color="#ff0000", is_active=True)
    result = await service.update_tag(tag_id, payload)

    assert result["success"] is False
    assert result["error_code"] == "no_changes"
    tag_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_tag_in_use_blocks_operation() -> None:
    tag_id = str(uuid4())
    existing = Tag(id=uuid4(), name="Urgente", color="#ff0000")

    tag_repository = MagicMock()
    tag_repository.find_by_id = AsyncMock(return_value=existing)

    appointment_repository = MagicMock()
    appointment_repository.count_by_tag = AsyncMock(return_value=3)

    service = TagService(tag_repository, appointment_repository)

    result = await service.delete_tag(tag_id)

    assert result["success"] is False
    assert result["error_code"] == "in_use"
    tag_repository.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_tag_success() -> None:
    tag_id = str(uuid4())
    existing = Tag(id=uuid4(), name="Urgente", color="#ff0000")

    tag_repository = MagicMock()
    tag_repository.find_by_id = AsyncMock(return_value=existing)
    tag_repository.delete = AsyncMock(return_value=True)

    appointment_repository = MagicMock()
    appointment_repository.count_by_tag = AsyncMock(return_value=0)

    service = TagService(tag_repository, appointment_repository)

    result = await service.delete_tag(tag_id)

    assert result["success"] is True
    tag_repository.delete.assert_awaited_with(tag_id)
