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
from .patient_document_dto import (
    ConfirmUploadRequestDTO,
    DownloadUrlResponseDTO,
    PatientDocumentDTO,
    PatientDocumentListResponseDTO,
    PresignUploadRequestDTO,
    PresignUploadResponseDTO,
)

__all__ = [
    "AppointmentCreateDTO",
    "AppointmentResponseDTO",
    "AppointmentFilterDTO",
    "AppointmentListResponseDTO",
    "ExcelUploadResponseDTO",
    "DashboardStatsDTO",
    "ConfirmUploadRequestDTO",
    "DownloadUrlResponseDTO",
    "PatientDocumentDTO",
    "PatientDocumentListResponseDTO",
    "PresignUploadRequestDTO",
    "PresignUploadResponseDTO",
]
