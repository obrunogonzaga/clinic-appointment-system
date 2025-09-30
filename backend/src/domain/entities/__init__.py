"""
Domain entities module.
"""

from .appointment import Appointment
from .car import Car
from .client import Client
from .collector import Collector
from .driver import Driver
from .tag import Tag, TagReference

__all__ = [
    "Appointment",
    "Car",
    "Client",
    "Collector",
    "Driver",
    "Tag",
    "TagReference",
]
