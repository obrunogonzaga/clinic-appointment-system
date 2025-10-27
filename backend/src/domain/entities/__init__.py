"""
Domain entities module.
"""

from .appointment import Appointment
from .car import Car
from .collector import Collector
from .driver import Driver
from .patient_document import PatientDocument, PatientDocumentStatus
from .tag import Tag, TagReference

__all__ = [
    "Appointment",
    "Car",
    "Collector",
    "Driver",
    "PatientDocument",
    "PatientDocumentStatus",
    "Tag",
    "TagReference",
]
