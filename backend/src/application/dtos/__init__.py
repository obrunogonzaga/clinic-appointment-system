"""
Data Transfer Objects (DTOs) for application layer.
"""

from .appointment_dto import (
    AppointmentCreateDTO,
    AppointmentFilterDTO,
    AppointmentListResponseDTO,
    AppointmentResponseDTO,
    DashboardStatsDTO,
    ExcelUploadResponseDTO,
)
from .tag_dto import (
    TagCreateDTO,
    TagListResponseDTO,
    TagResponseDTO,
    TagSummaryDTO,
    TagUpdateDTO,
)

__all__ = [
    "AppointmentCreateDTO",
    "AppointmentResponseDTO",
    "AppointmentFilterDTO",
    "AppointmentListResponseDTO",
    "ExcelUploadResponseDTO",
    "DashboardStatsDTO",
    "TagCreateDTO",
    "TagUpdateDTO",
    "TagResponseDTO",
    "TagListResponseDTO",
    "TagSummaryDTO",
]
