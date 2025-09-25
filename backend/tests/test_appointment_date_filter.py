from datetime import datetime, timedelta

from datetime import datetime

from src.application.dtos.appointment_dto import AppointmentScope
from src.application.services.appointment_service import AppointmentService
from src.application.services.excel_parser_service import ExcelParserService


class DummyRepo:  # Minimal stub; not used in these tests
    pass


def _make_service() -> AppointmentService:
    return AppointmentService(appointment_repository=DummyRepo(), excel_parser=ExcelParserService())


def test_parse_filter_date_accepts_iso_format():
    service = _make_service()
    start, end = service._parse_filter_date("2025-09-23")
    assert isinstance(start, datetime) and isinstance(end, datetime)
    assert start == datetime(2025, 9, 23)
    assert end == datetime(2025, 9, 24)


def test_parse_filter_date_accepts_brazilian_format():
    service = _make_service()
    start, end = service._parse_filter_date("23/09/2025")
    assert start == datetime(2025, 9, 23)
    assert end == datetime(2025, 9, 24)


def test_parse_filter_date_rejects_invalid_format():
    service = _make_service()
    try:
        service._parse_filter_date("09-23-2025")  # US format should be rejected
        assert False, "Expected ValueError for invalid format"
    except ValueError as e:
        assert "Formato de data inválido" in str(e)


def test_resolve_scope_bounds_current_uses_today_floor():
    service = _make_service()
    reference = datetime(2025, 1, 18, 12, 30)
    lower, upper = service._resolve_scope_bounds(
        AppointmentScope.CURRENT, reference=reference
    )
    assert lower == datetime(2025, 1, 18)
    assert upper is None


def test_resolve_scope_bounds_history_limits_upper_bound():
    service = _make_service()
    reference = datetime(2025, 1, 18, 12, 30)
    lower, upper = service._resolve_scope_bounds(
        AppointmentScope.HISTORY, reference=reference
    )
    assert lower is None
    assert upper == datetime(2025, 1, 18)


def test_merge_scope_with_dates_applies_lower_and_upper_limits():
    service = _make_service()
    reference = datetime(2025, 1, 18, 8, 0)
    parsed_dates = (datetime(2025, 1, 20), datetime(2025, 1, 25))
    scope_bounds = service._resolve_scope_bounds(
        AppointmentScope.CURRENT, reference=reference
    )
    merged = service._merge_scope_with_dates(parsed_dates, scope_bounds)
    # Lower bound should become the parsed value (as it is after today)
    assert merged[0] == datetime(2025, 1, 20)
    # Upper bound remains untouched
    assert merged[1] == datetime(2025, 1, 25)

    history_bounds = service._resolve_scope_bounds(
        AppointmentScope.HISTORY, reference=reference
    )
    merged_history = service._merge_scope_with_dates(parsed_dates, history_bounds)
    # Upper bound should be clamped to the start of the reference day
    assert merged_history[0] == datetime(2025, 1, 20)
    assert merged_history[1] == datetime(2025, 1, 18)

