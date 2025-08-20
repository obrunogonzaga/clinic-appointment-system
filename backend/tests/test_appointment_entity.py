"""
Tests for Appointment entity.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.domain.entities.appointment import Appointment


class TestAppointmentEntity:
    """Test cases for Appointment entity."""

    def test_create_valid_appointment(self):
        """Test creating a valid appointment with all required fields."""
        appointment = Appointment(
            nome_unidade="UBS Centro",
            nome_marca="Clínica Saúde",
            nome_paciente="João Silva",
            data_agendamento=datetime(2025, 1, 15),
            hora_agendamento="14:30",
        )

        assert appointment.nome_unidade == "UBS Centro"
        assert appointment.nome_marca == "Clínica Saúde"
        assert appointment.nome_paciente == "João Silva"
        assert appointment.data_agendamento == datetime(2025, 1, 15)
        assert appointment.hora_agendamento == "14:30"
        assert appointment.status == "Confirmado"  # Default value
        assert appointment.id is not None
        assert appointment.created_at is not None

    def test_create_appointment_with_optional_fields(self):
        """Test creating appointment with all fields including optional ones."""
        appointment = Appointment(
            nome_unidade="UBS Norte",
            nome_marca="Clínica Premium",
            nome_paciente="Maria Santos",
            data_agendamento=datetime(2025, 1, 20),
            hora_agendamento="09:00",
            tipo_consulta="Cardiologia",
            status="Reagendado",
            telefone="11999887766",
            carro="Honda Civic Prata",
            observacoes="Paciente com hipertensão",
        )

        assert appointment.tipo_consulta == "Cardiologia"
        assert appointment.status == "Reagendado"
        assert appointment.telefone == "11999887766"
        assert appointment.carro == "Honda Civic Prata"
        assert appointment.observacoes == "Paciente com hipertensão"

    def test_string_validation_strips_whitespace(self):
        """Test that string fields are properly trimmed."""
        appointment = Appointment(
            nome_unidade="  UBS Centro  ",
            nome_marca="  Clínica Saúde  ",
            nome_paciente="  João Silva  ",
            data_agendamento=datetime.now(),
            hora_agendamento="14:30",
        )

        assert appointment.nome_unidade == "UBS Centro"
        assert appointment.nome_marca == "Clínica Saúde"
        assert appointment.nome_paciente == "João Silva"

    def test_empty_required_fields_raises_error(self):
        """Test that empty required fields raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Appointment(
                nome_unidade="",
                nome_marca="Clínica",
                nome_paciente="João",
                data_agendamento=datetime.now(),
                hora_agendamento="14:30",
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("nome_unidade",) for e in errors)
        assert any(
            "Campo obrigatório não pode estar vazio" in e["msg"]
            for e in errors
        )

    def test_time_format_validation(self):
        """Test time format validation."""
        # Valid formats
        appointment = Appointment(
            nome_unidade="UBS",
            nome_marca="Clínica",
            nome_paciente="João",
            data_agendamento=datetime.now(),
            hora_agendamento="9:5",  # Should be normalized to 09:05
        )
        assert appointment.hora_agendamento == "09:05"

        # Invalid formats
        with pytest.raises(ValidationError) as exc_info:
            Appointment(
                nome_unidade="UBS",
                nome_marca="Clínica",
                nome_paciente="João",
                data_agendamento=datetime.now(),
                hora_agendamento="14:30:00",  # Seconds not allowed
            )

        errors = exc_info.value.errors()
        assert any(
            "Hora deve estar no formato HH:MM" in e["msg"] for e in errors
        )

    def test_time_range_validation(self):
        """Test that time values are within valid ranges."""
        # Invalid hour
        with pytest.raises(ValidationError) as exc_info:
            Appointment(
                nome_unidade="UBS",
                nome_marca="Clínica",
                nome_paciente="João",
                data_agendamento=datetime.now(),
                hora_agendamento="25:00",
            )

        errors = exc_info.value.errors()
        assert any("Hora deve estar entre 00 e 23" in e["msg"] for e in errors)

        # Invalid minutes
        with pytest.raises(ValidationError) as exc_info:
            Appointment(
                nome_unidade="UBS",
                nome_marca="Clínica",
                nome_paciente="João",
                data_agendamento=datetime.now(),
                hora_agendamento="14:60",
            )

        errors = exc_info.value.errors()
        assert any(
            "Minutos devem estar entre 00 e 59" in e["msg"] for e in errors
        )

    def test_phone_validation(self):
        """Test phone number validation and normalization."""
        # Valid phone numbers
        appointment = Appointment(
            nome_unidade="UBS",
            nome_marca="Clínica",
            nome_paciente="João",
            data_agendamento=datetime.now(),
            hora_agendamento="14:30",
            telefone="(11) 9 9988-7766",
        )
        assert appointment.telefone == "11999887766"  # Normalized

        # Phone with 10 digits (landline)
        appointment2 = Appointment(
            nome_unidade="UBS",
            nome_marca="Clínica",
            nome_paciente="João",
            data_agendamento=datetime.now(),
            hora_agendamento="14:30",
            telefone="1133334444",
        )
        assert appointment2.telefone == "1133334444"

        # Invalid phone (too short)
        with pytest.raises(ValidationError) as exc_info:
            Appointment(
                nome_unidade="UBS",
                nome_marca="Clínica",
                nome_paciente="João",
                data_agendamento=datetime.now(),
                hora_agendamento="14:30",
                telefone="123456",
            )

        errors = exc_info.value.errors()
        assert any(
            "Telefone deve ter 10 ou 11 dígitos" in e["msg"] for e in errors
        )

    def test_status_validation(self):
        """Test appointment status validation."""
        # Valid statuses
        valid_statuses = [
            "Confirmado",
            "Cancelado",
            "Reagendado",
            "Concluído",
            "Não Compareceu",
        ]

        for status in valid_statuses:
            appointment = Appointment(
                nome_unidade="UBS",
                nome_marca="Clínica",
                nome_paciente="João",
                data_agendamento=datetime.now(),
                hora_agendamento="14:30",
                status=status,
            )
            assert appointment.status == status

        # Invalid status
        with pytest.raises(ValidationError) as exc_info:
            Appointment(
                nome_unidade="UBS",
                nome_marca="Clínica",
                nome_paciente="João",
                data_agendamento=datetime.now(),
                hora_agendamento="14:30",
                status="Em Andamento",
            )

        errors = exc_info.value.errors()
        assert any("Status inválido" in e["msg"] for e in errors)

    def test_appointment_dict_representation(self):
        """Test appointment dictionary representation."""
        appointment = Appointment(
            nome_unidade="UBS Centro",
            nome_marca="Clínica Saúde",
            nome_paciente="João Silva",
            data_agendamento=datetime(2025, 1, 15),
            hora_agendamento="14:30",
            tipo_consulta="Clínico Geral",
        )

        data = appointment.model_dump()

        assert data["nome_unidade"] == "UBS Centro"
        assert data["nome_marca"] == "Clínica Saúde"
        assert data["nome_paciente"] == "João Silva"
        assert data["hora_agendamento"] == "14:30"
        assert data["tipo_consulta"] == "Clínico Geral"
        assert data["status"] == "Confirmado"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
