"""
Domain repository interfaces.
"""

from .appointment_repository_interface import AppointmentRepositoryInterface
from .car_repository_interface import CarRepositoryInterface
from .collector_repository_interface import CollectorRepositoryInterface
from .driver_repository_interface import DriverRepositoryInterface

__all__ = [
    "AppointmentRepositoryInterface",
    "CarRepositoryInterface",
    "CollectorRepositoryInterface",
    "DriverRepositoryInterface",
]
