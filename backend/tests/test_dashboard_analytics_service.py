import pytest
from unittest.mock import AsyncMock

from src.application.services.dashboard_analytics_service import (
    DashboardAnalyticsService,
)


@pytest.mark.asyncio
async def test_admin_dashboard_alerts_use_future_pending_count() -> None:
    appointment_repository = AsyncMock()
    appointment_repository.get_admin_dashboard_metrics = AsyncMock(
        return_value={
            "status_counts": {"Pendente": 10, "Confirmado": 5},
            "trend": [],
            "top_units": [],
            "resource_assignments": {},
            "total": 15,
            "pending_future_total": 3,
        }
    )

    driver_repository = AsyncMock()
    driver_repository.get_driver_stats = AsyncMock(
        return_value={"active_drivers": 0}
    )

    collector_repository = AsyncMock()
    collector_repository.get_collector_stats = AsyncMock(
        return_value={"active_collectors": 0}
    )

    car_repository = AsyncMock()
    car_repository.get_car_stats = AsyncMock(return_value={"active_cars": 0})

    service = DashboardAnalyticsService(
        appointment_repository,
        driver_repository,
        collector_repository,
        car_repository,
    )

    metrics = await service.get_admin_dashboard_metrics(period="7d")

    assert metrics["alerts"][0]["message"].startswith(
        "3 agendamentos aguardando ação da equipe"
    )
    appointment_repository.get_admin_dashboard_metrics.assert_awaited()
