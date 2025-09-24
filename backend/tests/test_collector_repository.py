from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.infrastructure.repositories.collector_repository import CollectorRepository


@pytest.mark.asyncio
async def test_find_by_cpf_handles_formatted_legacy_values():
    legacy_document = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "nome_completo": "Maria Silva",
        "cpf": "529.982.247-25",
        "telefone": "11987654321",
        "status": "Ativo",
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
    }

    collection = SimpleNamespace(
        find_one=AsyncMock(side_effect=[None, legacy_document])
    )
    repository = CollectorRepository(SimpleNamespace(collectors=collection))

    collector = await repository.find_by_cpf("529.982.247-25")

    assert collector is not None
    assert collector.cpf == "52998224725"
    assert collection.find_one.await_args_list[0].args[0] == {"cpf": "52998224725"}
    regex_query = collection.find_one.await_args_list[1].args[0]
    assert "$regex" in regex_query["cpf"]


@pytest.mark.asyncio
async def test_exists_by_cpf_handles_formatted_values():
    collection = SimpleNamespace(
        find_one=AsyncMock(side_effect=[None, {"_id": "abc123"}])
    )
    repository = CollectorRepository(SimpleNamespace(collectors=collection))

    exists = await repository.exists_by_cpf("529.982.247-25")

    assert exists is True
    assert collection.find_one.await_args_list[0].args[0] == {"cpf": "52998224725"}
    regex_query = collection.find_one.await_args_list[1].args[0]
    assert "$regex" in regex_query["cpf"]
