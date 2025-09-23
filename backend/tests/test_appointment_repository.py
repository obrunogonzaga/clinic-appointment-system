"""
Tests for AppointmentRepository.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient


pytestmark = pytest.mark.asyncio

from src.domain.entities.appointment import Appointment
from src.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
)


@pytest_asyncio.fixture
async def test_database():
    """Create a test database instance."""
    # Use test database to avoid conflicts
    client = AsyncMongoMockClient()
    db = client.get_database("clinic_test")

    # Clean up before test
    await db.appointments.delete_many({})

    yield db

    # Clean up after test
    await db.appointments.delete_many({})
    await client.drop_database("clinic_test")


@pytest_asyncio.fixture
async def repository(test_database):
    """Create repository instance with test database."""
    repo = AppointmentRepository(test_database)
    await repo.create_indexes()
    return repo


@pytest.fixture
def sample_appointment():
    """Create a sample appointment for testing."""
    return Appointment(
        nome_unidade="UBS Centro",
        nome_marca="Clínica Saúde",
        nome_paciente="João Silva",
        data_agendamento=datetime(2025, 1, 15),
        hora_agendamento="14:30",
        tipo_consulta="Clínico Geral",
        status="Confirmado",
        telefone="11999887766",
        carro="Honda Civic Prata",
        observacoes="Primeira consulta",
    )


class TestAppointmentRepository:
    """Test cases for AppointmentRepository."""

    async def test_create_appointment(
        self,
        repository: AppointmentRepository,
        sample_appointment: Appointment,
    ):
        """Test creating a single appointment."""
        created = await repository.create(sample_appointment)

        assert created.id == sample_appointment.id
        assert created.nome_unidade == "UBS Centro"
        assert created.nome_paciente == "João Silva"

        # Verify it was stored in database
        found = await repository.find_by_id(str(created.id))
        assert found is not None
        assert found.nome_unidade == "UBS Centro"

    async def test_create_many_appointments(
        self, repository: AppointmentRepository
    ):
        """Test creating multiple appointments in bulk."""
        appointments = [
            Appointment(
                nome_unidade="UBS Norte",
                nome_marca="Clínica A",
                nome_paciente=f"Paciente {i}",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="10:00",
            )
            for i in range(3)
        ]

        created = await repository.create_many(appointments)

        assert len(created) == 3
        for appointment in created:
            assert appointment.nome_unidade == "UBS Norte"

        # Verify all were stored
        count = await repository.count()
        assert count == 3

    async def test_find_by_id(
        self,
        repository: AppointmentRepository,
        sample_appointment: Appointment,
    ):
        """Test finding appointment by ID."""
        await repository.create(sample_appointment)

        found = await repository.find_by_id(str(sample_appointment.id))
        assert found is not None
        assert found.id == sample_appointment.id
        assert found.nome_paciente == "João Silva"

        # Test non-existent ID
        not_found = await repository.find_by_id(str(uuid4()))
        assert not_found is None

    async def test_find_all_with_pagination(
        self, repository: AppointmentRepository
    ):
        """Test finding all appointments with pagination."""
        # Create multiple appointments
        appointments = [
            Appointment(
                nome_unidade="UBS Centro",
                nome_marca="Clínica",
                nome_paciente=f"Paciente {i}",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="10:00",
            )
            for i in range(5)
        ]
        await repository.create_many(appointments)

        # Test pagination
        page1 = await repository.find_all(skip=0, limit=2)
        assert len(page1) == 2

        page2 = await repository.find_all(skip=2, limit=2)
        assert len(page2) == 2

        # Verify different results
        page1_ids = {str(a.id) for a in page1}
        page2_ids = {str(a.id) for a in page2}
        assert page1_ids.isdisjoint(page2_ids)

    async def test_find_by_filters(self, repository: AppointmentRepository):
        """Test finding appointments by specific filters."""
        # Create appointments with different attributes
        appointments = [
            Appointment(
                nome_unidade="UBS Centro",
                nome_marca="Clínica A",
                nome_paciente="João Silva",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="10:00",
                status="Confirmado",
            ),
            Appointment(
                nome_unidade="UBS Norte",
                nome_marca="Clínica B",
                nome_paciente="Maria Santos",
                data_agendamento=datetime(2025, 1, 20),
                hora_agendamento="14:00",
                status="Cancelado",
            ),
            Appointment(
                nome_unidade="UBS Centro",
                nome_marca="Clínica A",
                nome_paciente="Pedro Costa",
                data_agendamento=datetime(2025, 1, 25),
                hora_agendamento="09:00",
                status="Confirmado",
            ),
        ]
        await repository.create_many(appointments)

        # Test filter by unit
        centro_appointments = await repository.find_by_filters(
            nome_unidade="UBS Centro"
        )
        assert len(centro_appointments) == 2

        # Test filter by brand
        clinica_a = await repository.find_by_filters(nome_marca="Clínica A")
        assert len(clinica_a) == 2

        # Test filter by status
        confirmed = await repository.find_by_filters(status="Confirmado")
        assert len(confirmed) == 2

        # Test filter by date range
        date_filtered = await repository.find_by_filters(
            data_inicio=datetime(2025, 1, 18), data_fim=datetime(2025, 1, 22)
        )
        assert len(date_filtered) == 1
        assert date_filtered[0].nome_paciente == "Maria Santos"

        # Test combined filters
        combined = await repository.find_by_filters(
            nome_unidade="UBS Centro", status="Confirmado"
        )
        assert len(combined) == 2

    async def test_count_appointments(self, repository: AppointmentRepository):
        """Test counting appointments."""
        # Empty database
        count = await repository.count()
        assert count == 0

        # Create some appointments
        appointments = [
            Appointment(
                nome_unidade="UBS Centro",
                nome_marca="Clínica",
                nome_paciente=f"Paciente {i}",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="10:00",
            )
            for i in range(3)
        ]
        await repository.create_many(appointments)

        # Test count
        count = await repository.count()
        assert count == 3

        # Test count with filters
        count_filtered = await repository.count({"nome_unidade": "UBS Centro"})
        assert count_filtered == 3

    async def test_update_appointment(
        self,
        repository: AppointmentRepository,
        sample_appointment: Appointment,
    ):
        """Test updating an appointment."""
        await repository.create(sample_appointment)

        # Update appointment
        update_data = {
            "status": "Alterar",
            "carro": "Toyota Corolla Azul",
            "observacoes": "Reagendado pelo paciente",
        }

        updated = await repository.update(
            str(sample_appointment.id), update_data
        )

        assert updated is not None
        assert updated.status == "Alterar"
        assert updated.carro == "Toyota Corolla Azul"
        assert updated.observacoes == "Reagendado pelo paciente"
        assert updated.updated_at is not None

        # Test update non-existent appointment
        not_updated = await repository.update(
            str(uuid4()), {"status": "Cancelado"}
        )
        assert not_updated is None

    async def test_delete_appointment(
        self,
        repository: AppointmentRepository,
        sample_appointment: Appointment,
    ):
        """Test deleting an appointment."""
        await repository.create(sample_appointment)

        # Verify exists
        found = await repository.find_by_id(str(sample_appointment.id))
        assert found is not None

        # Delete
        deleted = await repository.delete(str(sample_appointment.id))
        assert deleted is True

        # Verify deleted
        not_found = await repository.find_by_id(str(sample_appointment.id))
        assert not_found is None

        # Test delete non-existent
        not_deleted = await repository.delete(str(uuid4()))
        assert not_deleted is False

    async def test_delete_many_appointments(
        self, repository: AppointmentRepository
    ):
        """Test deleting multiple appointments."""
        # Create appointments
        appointments = [
            Appointment(
                nome_unidade="UBS Centro",
                nome_marca="Clínica",
                nome_paciente=f"Paciente {i}",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="10:00",
                status="Confirmado" if i % 2 == 0 else "Cancelado",
            )
            for i in range(4)
        ]
        await repository.create_many(appointments)

        # Delete all cancelled appointments
        deleted_count = await repository.delete_many({"status": "Cancelado"})
        assert deleted_count == 2

        # Verify remaining appointments
        remaining = await repository.count()
        assert remaining == 2

    async def test_get_distinct_values(
        self, repository: AppointmentRepository
    ):
        """Test getting distinct values for fields."""
        # Create appointments with different values
        appointments = [
            Appointment(
                nome_unidade="UBS Centro",
                nome_marca="Clínica A",
                nome_paciente="João",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="10:00",
            ),
            Appointment(
                nome_unidade="UBS Norte",
                nome_marca="Clínica B",
                nome_paciente="Maria",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="11:00",
            ),
            Appointment(
                nome_unidade="UBS Centro",  # Duplicate
                nome_marca="Clínica A",  # Duplicate
                nome_paciente="Pedro",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="12:00",
            ),
        ]
        await repository.create_many(appointments)

        # Test distinct units
        units = await repository.get_distinct_values("nome_unidade")
        assert len(units) == 2
        assert "UBS Centro" in units
        assert "UBS Norte" in units

        # Test distinct brands
        brands = await repository.get_distinct_values("nome_marca")
        assert len(brands) == 2
        assert "Clínica A" in brands
        assert "Clínica B" in brands

    async def test_get_appointment_stats(
        self, repository: AppointmentRepository
    ):
        """Test getting appointment statistics."""
        # Empty database
        stats = await repository.get_appointment_stats()
        assert stats["total_appointments"] == 0
        assert stats["confirmed_appointments"] == 0
        assert stats["cancelled_appointments"] == 0

        # Create appointments with different statuses
        appointments = [
            Appointment(
                nome_unidade="UBS Centro",
                nome_marca="Clínica A",
                nome_paciente="João",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="10:00",
                status="Confirmado",
            ),
            Appointment(
                nome_unidade="UBS Norte",
                nome_marca="Clínica B",
                nome_paciente="Maria",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="11:00",
                status="Cancelado",
            ),
            Appointment(
                nome_unidade="UBS Centro",
                nome_marca="Clínica A",
                nome_paciente="Pedro",
                data_agendamento=datetime(2025, 1, 15),
                hora_agendamento="12:00",
                status="Confirmado",
            ),
        ]
        await repository.create_many(appointments)

        # Test statistics
        stats = await repository.get_appointment_stats()
        assert stats["total_appointments"] == 3
        assert stats["confirmed_appointments"] == 2
        assert stats["cancelled_appointments"] == 1
        assert stats["total_units"] == 2
        assert stats["total_brands"] == 2
