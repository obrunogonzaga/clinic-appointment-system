"""
Infrastructure repository implementations.
"""

from .appointment_repository import AppointmentRepository
from .patient_document_repository import PatientDocumentRepository
from .tag_repository import TagRepository

__all__ = [
    "AppointmentRepository",
    "PatientDocumentRepository",
    "TagRepository",
]
