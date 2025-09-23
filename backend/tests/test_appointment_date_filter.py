from datetime import datetime, timedelta

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

