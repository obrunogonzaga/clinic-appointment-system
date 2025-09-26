"""
Data Transfer Objects (DTOs) for application layer.
"""

from .appointment_dto import (
    AppointmentCreateDTO,
    AppointmentFilterDTO,
    AppointmentListResponseDTO,
    AppointmentResponseDTO,
    AppointmentScope,
    DashboardStatsDTO,
    ExcelUploadResponseDTO,
)
from .patient_document_dto import (
    PatientDocumentConfirmRequestDTO,
    PatientDocumentDownloadURLDTO,
    PatientDocumentMetadataDTO,
    PatientDocumentPresignRequestDTO,
    PatientDocumentPresignResponseDTO,
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
    "AppointmentScope",
    "ExcelUploadResponseDTO",
    "DashboardStatsDTO",
    "PatientDocumentConfirmRequestDTO",
    "PatientDocumentDownloadURLDTO",
    "PatientDocumentMetadataDTO",
    "PatientDocumentPresignRequestDTO",
    "PatientDocumentPresignResponseDTO",
    "TagCreateDTO",
    "TagUpdateDTO",
    "TagResponseDTO",
    "TagListResponseDTO",
    "TagSummaryDTO",
]
