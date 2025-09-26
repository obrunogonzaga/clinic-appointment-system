"""Service that consolidates analytics for the administrative dashboard."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.domain.repositories.appointment_repository_interface import (
    AppointmentRepositoryInterface,
)
from src.domain.repositories.car_repository_interface import (
    CarRepositoryInterface,
)
from src.domain.repositories.collector_repository_interface import (
    CollectorRepositoryInterface,
)
from src.domain.repositories.driver_repository_interface import (
    DriverRepositoryInterface,
)


class DashboardAnalyticsService:
    """Compose appointment and resource data into dashboard-friendly insights."""

    _CONFIRMED_STATUSES: Sequence[str] = ("Confirmado", "Coletado")
    _CANCELLATION_STATUSES: Sequence[str] = ("Cancelado",)
    _NO_SHOW_STATUSES: Sequence[str] = (
        "No-show",
        "No Show",
        "No-Show",
        "Não compareceu",
        "Nao compareceu",
    )
    _PENDING_STATUSES: Sequence[str] = (
        "Pendente",
        "Autorização",
        "Cadastrar",
        "Agendado",
        "Alterar",
        "Recoleta",
    )

    def __init__(
        self,
        appointment_repository: AppointmentRepositoryInterface,
        driver_repository: DriverRepositoryInterface,
        collector_repository: CollectorRepositoryInterface,
        car_repository: CarRepositoryInterface,
    ) -> None:
        self.appointment_repository = appointment_repository
        self.driver_repository = driver_repository
        self.collector_repository = collector_repository
        self.car_repository = car_repository

    async def get_admin_dashboard_metrics(
        self,
        period: str = "30d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return normalized metrics for the administrative dashboard."""

        period_start, period_end = self._resolve_period(period, start_date, end_date)

        (
            appointment_metrics,
            driver_stats,
            collector_stats,
            car_stats,
        ) = await asyncio.gather(
            self.appointment_repository.get_admin_dashboard_metrics(
                period_start, period_end
            ),
            self.driver_repository.get_driver_stats(),
            self.collector_repository.get_collector_stats(),
            self.car_repository.get_car_stats(),
        )

        status_counts: Dict[str, int] = appointment_metrics.get("status_counts", {})
        total_appointments = appointment_metrics.get("total", 0)
        trend_points = appointment_metrics.get("trend", [])
        top_units_raw = appointment_metrics.get("top_units", [])
        assignments = appointment_metrics.get("resource_assignments", {})

        normalized_trend = self._fill_trend(period_start, period_end, trend_points)
        trend_values = [point["value"] for point in normalized_trend]
        overall_trend = self._compute_trend_variation(trend_values)

        confirmed_count = self._sum_statuses(status_counts, self._CONFIRMED_STATUSES)
        cancelled_count = self._sum_statuses(status_counts, self._CANCELLATION_STATUSES)
        no_show_count = self._sum_statuses(status_counts, self._NO_SHOW_STATUSES)
        pending_count = self._sum_statuses(status_counts, self._PENDING_STATUSES)

        confirmation_rate = self._compute_percentage(
            confirmed_count, total_appointments
        )
        cancellation_rate = self._compute_percentage(
            cancelled_count, total_appointments
        )

        kpis = [
            {
                "label": "Agendamentos",
                "value": total_appointments,
                "trend": overall_trend,
            },
            {
                "label": "Taxa de confirmação",
                "value": confirmation_rate,
                "trend": overall_trend,
            },
            {"label": "No-show", "value": no_show_count},
            {"label": "Cancelamentos", "value": cancelled_count},
        ]

        resource_utilization = self._build_resource_utilization(
            assignments,
            driver_stats,
            collector_stats,
            car_stats,
        )

        alerts = self._compose_alerts(
            pending_count,
            no_show_count,
            cancellation_rate,
            confirmation_rate,
        )

        return {
            "success": True,
            "kpis": kpis,
            "trend": normalized_trend,
            "top_units": self._normalize_top_units(top_units_raw),
            "resource_utilization": resource_utilization,
            "alerts": alerts,
            "period": {
                "start": period_start.isoformat(),
                "end": (period_end - timedelta(seconds=1)).isoformat(),
            },
        }

    def _resolve_period(
        self, period: str, start_date: Optional[str], end_date: Optional[str]
    ) -> Tuple[datetime, datetime]:
        if start_date and end_date:
            start = self._parse_date(start_date)
            end = self._parse_date(end_date) + timedelta(days=1)
            return start, end

        days = self._parse_period_days(period)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = today + timedelta(days=1)
        period_start = period_end - timedelta(days=days)
        return period_start, period_end

    @staticmethod
    def _parse_period_days(period: str) -> int:
        if not period:
            return 30
        value = period.strip().lower()
        if value.endswith("d"):
            number = value[:-1]
        else:
            number = value
        try:
            days = int(number)
        except ValueError:
            return 30
        return max(1, days)

    @staticmethod
    def _parse_date(raw_date: str) -> datetime:
        cleaned = raw_date.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                parsed = datetime.strptime(cleaned, fmt)
                return parsed.replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                continue
        raise ValueError("Formato de data inválido. Use YYYY-MM-DD ou DD/MM/YYYY")

    @staticmethod
    def _fill_trend(
        start: datetime, end: datetime, points: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        lookup = {point["date"]: int(point["value"]) for point in points}
        result: List[Dict[str, Any]] = []
        cursor = start
        while cursor < end:
            label = cursor.strftime("%Y-%m-%d")
            result.append({"date": label, "value": lookup.get(label, 0)})
            cursor += timedelta(days=1)
        return result

    @staticmethod
    def _compute_trend_variation(values: List[int]) -> float:
        if not values:
            return 0.0
        midpoint = max(1, len(values) // 2)
        first_half = sum(values[:midpoint])
        second_half = sum(values[midpoint:])
        if first_half == 0:
            return 100.0 if second_half > 0 else 0.0
        variation = ((second_half - first_half) / first_half) * 100
        return round(variation, 2)

    @staticmethod
    def _sum_statuses(status_counts: Dict[str, int], statuses: Sequence[str]) -> int:
        normalized = {key.lower(): value for key, value in status_counts.items()}
        total = 0
        for status in statuses:
            total += normalized.get(status.lower(), 0)
        return total

    @staticmethod
    def _compute_percentage(partial: int, total: int) -> float:
        if total <= 0:
            return 0.0
        return round((partial / total) * 100, 2)

    def _normalize_top_units(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for item in items:
            unit = item.get("unit") or "Unidade não informada"
            brand = item.get("brand") or ""
            count = int(item.get("count", 0))

            if brand and brand != unit and "não informada" not in brand.lower():
                name = f"{unit} · {brand}"
            else:
                name = unit

            normalized.append({"name": name, "value": count})
        return normalized

    def _build_resource_utilization(
        self,
        assignments: Dict[str, Any],
        driver_stats: Dict[str, Any],
        collector_stats: Dict[str, Any],
        car_stats: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        def compute_utilization(assigned: int, active: int) -> float:
            if active <= 0:
                return 0.0
            percentage = (assigned / active) * 100
            return round(min(percentage, 100.0), 2)

        return [
            {
                "label": "Motoristas",
                "utilization": compute_utilization(
                    int(assignments.get("drivers", 0)),
                    int(driver_stats.get("active_drivers", 0)),
                ),
            },
            {
                "label": "Coletoras",
                "utilization": compute_utilization(
                    int(assignments.get("collectors", 0)),
                    int(collector_stats.get("active_collectors", 0)),
                ),
            },
            {
                "label": "Carros",
                "utilization": compute_utilization(
                    int(assignments.get("cars", 0)),
                    int(car_stats.get("active_cars", 0)),
                ),
            },
        ]

    @staticmethod
    def _compose_alerts(
        pending: int,
        no_show: int,
        cancellation_rate: float,
        confirmation_rate: float,
    ) -> List[Dict[str, str]]:
        alerts: List[Dict[str, str]] = []

        if pending > 0:
            alerts.append(
                {
                    "id": "pending-appointments",
                    "message": f"{pending} agendamentos aguardando ação da equipe.",
                    "type": "warning",
                }
            )

        if cancellation_rate >= 10:
            alerts.append(
                {
                    "id": "high-cancellation-rate",
                    "message": (
                        "Taxa de cancelamento acima de 10%. Avalie possíveis causas."
                    ),
                    "type": "warning",
                }
            )
        elif cancellation_rate > 0:
            alerts.append(
                {
                    "id": "cancellation-activity",
                    "message": (
                        f"Taxa de cancelamento atual em {cancellation_rate}% do período."
                    ),
                    "type": "info",
                }
            )

        if no_show > 0:
            alerts.append(
                {
                    "id": "no-show-detected",
                    "message": f"{no_show} ocorrências de no-show registradas.",
                    "type": "warning",
                }
            )

        if confirmation_rate < 50:
            alerts.append(
                {
                    "id": "low-confirmation",
                    "message": "Taxa de confirmação abaixo de 50%. Reforce o follow-up.",
                    "type": "warning",
                }
            )

        return alerts
