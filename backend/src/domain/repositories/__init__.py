"""
Domain repository interfaces.
"""

from .appointment_repository_interface import AppointmentRepositoryInterface
from .car_repository_interface import CarRepositoryInterface
from .client_repository_interface import ClientRepositoryInterface
from .collector_repository_interface import CollectorRepositoryInterface
from .driver_repository_interface import DriverRepositoryInterface
from .tag_repository_interface import TagRepositoryInterface

__all__ = [
    "AppointmentRepositoryInterface",
    "CarRepositoryInterface",
    "ClientRepositoryInterface",
    "CollectorRepositoryInterface",
    "DriverRepositoryInterface",
    "TagRepositoryInterface",
]
