import pytest
from unittest.mock import AsyncMock

from src.application.dtos.collector_dto import CollectorCreateDTO
from src.application.services.collector_service import CollectorService
from src.domain.entities.collector import Collector


@pytest.mark.asyncio
async def test_create_collector_normalizes_cpf_before_uniqueness_check():
    repository = AsyncMock()
    repository.find_by_cpf.return_value = None

    stored_collector = Collector(
        nome_completo="Maria Silva",
        cpf="52998224725",
        telefone="11987654321",
        email="maria@example.com",
    )
    repository.create.return_value = stored_collector

    service = CollectorService(repository)

    dto = CollectorCreateDTO(
        nome_completo="Maria Silva",
        cpf="529.982.247-25",
        telefone="(11) 98765-4321",
        email="maria@example.com",
        status="Ativo",
    )

    result = await service.create_collector(dto)

    repository.find_by_cpf.assert_awaited_once_with("52998224725")
    repository.create.assert_awaited_once()
    assert result["success"] is True
    assert result["collector"].cpf == "52998224725"
