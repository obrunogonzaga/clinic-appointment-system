"""Tests for appointment origin field."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.domain.entities.appointment import Appointment, AppointmentOrigin


def test_appointment_default_origin_is_manual():
    """Test that default origin is Manual."""
    appointment = Appointment(
        nome_unidade="UBS Centro",
        nome_marca="Clínica Saúde",
        nome_paciente="João Silva",
    )
    assert appointment.origin == AppointmentOrigin.MANUAL


def test_appointment_can_set_dasa_origin():
    """Test that we can set DASA origin."""
    appointment = Appointment(
        nome_unidade="UBS Centro",
        nome_marca="Clínica Saúde",
        nome_paciente="João Silva",
        origin=AppointmentOrigin.DASA,
    )
    assert appointment.origin == AppointmentOrigin.DASA


def test_appointment_origin_serialization():
    """Test that origin is properly serialized."""
    appointment = Appointment(
        nome_unidade="UBS Centro",
        nome_marca="Clínica Saúde",
        nome_paciente="João Silva",
        origin=AppointmentOrigin.DASA,
    )
    data = appointment.model_dump()
    assert data["origin"] == "DASA"
    assert isinstance(data["origin"], str)


def test_appointment_origin_from_string():
    """Test creating appointment with string origin."""
    appointment = Appointment(
        nome_unidade="UBS Centro",
        nome_marca="Clínica Saúde",
        nome_paciente="João Silva",
        origin="DASA",
    )
    assert appointment.origin == AppointmentOrigin.DASA


def test_appointment_manual_origin_explicit():
    """Test explicitly setting Manual origin."""
    appointment = Appointment(
        nome_unidade="UBS Centro",
        nome_marca="Clínica Saúde",
        nome_paciente="João Silva",
        origin=AppointmentOrigin.MANUAL,
    )
    assert appointment.origin == AppointmentOrigin.MANUAL


def test_appointment_origin_enum_values():
    """Test that enum has correct values."""
    assert AppointmentOrigin.DASA.value == "DASA"
    assert AppointmentOrigin.MANUAL.value == "Manual"
