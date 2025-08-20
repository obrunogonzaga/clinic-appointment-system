"""
Tests for Excel parser service.
"""

import io
from datetime import datetime

import pandas as pd
import pytest

from src.application.services.excel_parser_service import ExcelParserService


class TestExcelParserService:
    """Test cases for Excel parser service."""

    @pytest.fixture
    def parser_service(self):
        """Create parser service instance."""
        return ExcelParserService()

    @pytest.fixture
    def sample_excel_data(self):
        """Create sample Excel data for testing."""
        return {
            "Nome da Marca": ["Clínica A", "Clínica B", "Clínica A"],
            "Nome da Unidade": ["UBS Centro", "UBS Norte", "UBS Sul"],
            "Nome do Paciente": ["João Silva", "Maria Santos", "Pedro Costa"],
            "Data/Hora Início Agendamento": [
                "15/01/2025 14:30",
                "16/01/2025 10:00",
                "17/01/2025 16:45",
            ],
            "Status Agendamento": ["Confirmado", "Cancelado", "Agendado"],
            "Contato(s) do Paciente": [
                "11999887766",
                "(11) 9 8877-6655",
                "11 98765-4321",
            ],
            "Observação": ["Primeira consulta", None, "Retorno"],
            "Nomes dos Exames": [
                "Clínico Geral",
                "Cardiologia",
                "Dermatologia",
            ],
        }

    def create_excel_file(self, data: dict) -> io.BytesIO:
        """Create Excel file from data."""
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        return buffer

    @pytest.mark.asyncio
    async def test_parse_valid_excel_file(
        self, parser_service: ExcelParserService, sample_excel_data
    ):
        """Test parsing valid Excel file."""
        excel_file = self.create_excel_file(sample_excel_data)

        result = await parser_service.parse_excel_file(excel_file, "test.xlsx")

        assert result.success is True
        assert result.total_rows == 3
        assert result.valid_rows == 3
        assert result.invalid_rows == 0
        assert len(result.appointments) == 3

        # Test first appointment
        appointment = result.appointments[0]
        assert appointment.nome_marca == "Clínica A"
        assert appointment.nome_unidade == "UBS Centro"
        assert appointment.nome_paciente == "João Silva"
        assert appointment.data_agendamento == datetime(2025, 1, 15)
        assert appointment.hora_agendamento == "14:30"
        assert appointment.status == "Confirmado"
        assert appointment.telefone == "11999887766"
        assert (
            appointment.carro is None
        )  # Não há campo "Nome da Sala" neste teste
        assert (
            appointment.observacoes == "Primeira consulta"
        )  # Campo "Observação" da planilha
        assert appointment.tipo_consulta == "Clínico Geral"

    @pytest.mark.asyncio
    async def test_parse_excel_with_observacoes_field(
        self, parser_service: ExcelParserService
    ):
        """Test parsing Excel with both 'Observação' and 'Observações' fields."""
        data = {
            "Nome da Marca": ["Clínica A"],
            "Nome da Unidade": ["UBS Centro"],
            "Nome do Paciente": ["João Silva"],
            "Data/Hora Início Agendamento": ["15/01/2025 14:30"],
            "Status Agendamento": ["Confirmado"],
            "Contato(s) do Paciente": ["11999887766"],
            "Observação": ["Carro: Honda Civic"],  # Mapeia para campo 'carro'
            "Observações": [
                "Paciente diabético"
            ],  # Mapeia para campo 'observacoes'
            "Nomes dos Exames": ["Clínico Geral"],
        }

        excel_file = self.create_excel_file(data)

        result = await parser_service.parse_excel_file(excel_file, "test.xlsx")

        assert result.success is True
        assert len(result.appointments) == 1

        appointment = result.appointments[0]
        assert (
            appointment.carro is None
        )  # Não há campo "Nome da Sala" neste teste
        assert (
            appointment.observacoes == "Paciente diabético"
        )  # Campo "Observações" tem prioridade

    @pytest.mark.asyncio
    async def test_parse_excel_with_nome_da_sala_field(
        self, parser_service: ExcelParserService
    ):
        """Test parsing Excel with 'Nome da Sala' field containing car info."""
        data = {
            "Nome da Marca": ["Clínica A"],
            "Nome da Unidade": ["UBS Centro"],
            "Nome do Paciente": ["João Silva"],
            "Data/Hora Início Agendamento": ["15/01/2025 14:30"],
            "Status Agendamento": ["Confirmado"],
            "Contato(s) do Paciente": ["11999887766"],
            "Observação": ["o exame pede anti-hiv"],  # Vai para observacoes
            "Nome da Sala": [
                "AD-SF-FQ-AC-AV CENTER 3 CARRO 1 - UND84"
            ],  # Extrai carro
            "Nomes dos Exames": ["Clínico Geral"],
        }

        excel_file = self.create_excel_file(data)

        result = await parser_service.parse_excel_file(excel_file, "test.xlsx")

        assert result.success is True
        assert len(result.appointments) == 1

        appointment = result.appointments[0]
        assert (
            appointment.carro == "CENTER 3 CARRO 1 - UND84"
        )  # Extraído do Nome da Sala
        assert (
            appointment.observacoes == "o exame pede anti-hiv"
        )  # Do campo Observação

    @pytest.mark.asyncio
    async def test_parse_excel_with_missing_columns(
        self, parser_service: ExcelParserService
    ):
        """Test parsing Excel file with missing required columns."""
        # Missing required column
        data = {
            "Nome da Marca": ["Clínica A"],
            "Nome da Unidade": ["UBS Centro"],
            # Missing "Nome do Paciente"
            "Data/Hora Início Agendamento": ["15/01/2025 14:30"],
        }

        excel_file = self.create_excel_file(data)

        result = await parser_service.parse_excel_file(excel_file, "test.xlsx")

        assert result.success is False
        assert "Colunas obrigatórias não encontradas" in result.errors[0]

    @pytest.mark.asyncio
    async def test_parse_excel_with_invalid_data(
        self, parser_service: ExcelParserService
    ):
        """Test parsing Excel file with invalid data."""
        data = {
            "Nome da Marca": ["Clínica A", ""],  # Empty required field
            "Nome da Unidade": ["UBS Centro", "UBS Norte"],
            "Nome do Paciente": ["João Silva", "Maria Santos"],
            "Data/Hora Início Agendamento": [
                "15/01/2025 14:30",
                "invalid_date",
            ],  # Invalid date
            "Status Agendamento": ["Confirmado", "Confirmado"],
            "Contato(s) do Paciente": ["11999887766", "123"],  # Invalid phone
            "Observação": ["OK", "OK"],
            "Nomes dos Exames": ["Clínico Geral", "Cardiologia"],
        }

        excel_file = self.create_excel_file(data)

        result = await parser_service.parse_excel_file(excel_file, "test.xlsx")

        assert result.total_rows == 2
        assert result.valid_rows == 1  # Only first row is valid
        assert result.invalid_rows == 1
        assert len(result.appointments) == 1
        assert len(result.errors) == 1
        assert "Linha 2" in result.errors[0]

    @pytest.mark.asyncio
    async def test_clean_string_method(
        self, parser_service: ExcelParserService
    ):
        """Test string cleaning method."""
        # Test normal string
        assert (
            parser_service._clean_string("  Normal String  ")
            == "Normal String"
        )

        # Test empty/None values
        assert parser_service._clean_string("") is None
        assert parser_service._clean_string("   ") is None
        assert parser_service._clean_string(None) is None

        # Test pandas NaN
        import numpy as np

        assert parser_service._clean_string(np.nan) is None

    @pytest.mark.asyncio
    async def test_clean_phone_method(
        self, parser_service: ExcelParserService
    ):
        """Test phone cleaning method."""
        # Test various phone formats
        assert parser_service._clean_phone("(11) 9 9988-7766") == "11999887766"
        assert (
            parser_service._clean_phone("+55 11 99988-7766") == "11999887766"
        )
        assert parser_service._clean_phone("11 99988-7766") == "11999887766"

        # Test multiple phones (semicolon separated)
        assert (
            parser_service._clean_phone("11999887766;11988776655")
            == "11999887766"
        )

        # Test invalid phones
        assert parser_service._clean_phone("123") is None
        assert parser_service._clean_phone("") is None
        assert parser_service._clean_phone(None) is None

    @pytest.mark.asyncio
    async def test_parse_datetime_method(
        self, parser_service: ExcelParserService
    ):
        """Test datetime parsing method."""
        # Test string format
        date, time = parser_service._parse_datetime("15/01/2025 14:30")
        assert date == datetime(2025, 1, 15)
        assert time == "14:30"

        # Test datetime object
        dt = datetime(2025, 1, 15, 14, 30)
        date, time = parser_service._parse_datetime(dt)
        assert date == datetime(2025, 1, 15)
        assert time == "14:30"

        # Test invalid datetime
        with pytest.raises(ValueError):
            parser_service._parse_datetime("invalid_date")

        # Test None/empty
        with pytest.raises(ValueError):
            parser_service._parse_datetime(None)

    @pytest.mark.asyncio
    async def test_map_status_method(self, parser_service: ExcelParserService):
        """Test status mapping method."""
        # Test valid statuses
        assert parser_service._map_status("Confirmado") == "Confirmado"
        assert parser_service._map_status("Cancelado") == "Cancelado"
        assert parser_service._map_status("Agendado") == "Confirmado"  # Mapped
        assert (
            parser_service._map_status("Efetivado") == "Confirmado"
        )  # Mapped

        # Test invalid/None status
        assert parser_service._map_status("Unknown") == "Confirmado"  # Default
        assert parser_service._map_status(None) == "Confirmado"  # Default
        assert parser_service._map_status("") == "Confirmado"  # Default

    @pytest.mark.asyncio
    async def test_get_file_info(
        self, parser_service: ExcelParserService, sample_excel_data
    ):
        """Test getting file information."""
        excel_file = self.create_excel_file(sample_excel_data)

        info = parser_service.get_file_info(excel_file, "test.xlsx")

        assert info["filename"] == "test.xlsx"
        assert info["total_rows"] == 3
        assert info["total_columns"] == 8
        assert info["has_required_columns"] is True
        assert "Nome da Marca" in info["columns"]
        assert "Nome da Unidade" in info["columns"]
        assert "Nome do Paciente" in info["columns"]

    @pytest.mark.asyncio
    async def test_parse_empty_excel_file(
        self, parser_service: ExcelParserService
    ):
        """Test parsing empty Excel file."""
        # Create empty DataFrame
        df = pd.DataFrame()
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        result = await parser_service.parse_excel_file(buffer, "empty.xlsx")

        assert result.success is False
        assert "Arquivo Excel está vazio" in result.errors[0]

    @pytest.mark.asyncio
    async def test_parse_csv_file(
        self, parser_service: ExcelParserService, sample_excel_data
    ):
        """Test parsing CSV file."""
        df = pd.DataFrame(sample_excel_data)
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, encoding="utf-8")
        buffer.seek(0)

        result = await parser_service.parse_excel_file(buffer, "test.csv")

        assert result.success is True
        assert result.total_rows == 3
        assert result.valid_rows == 3
        assert len(result.appointments) == 3

    @pytest.mark.asyncio
    async def test_parse_unsupported_file_format(
        self, parser_service: ExcelParserService
    ):
        """Test parsing unsupported file format."""
        buffer = io.BytesIO(b"some text content")

        result = await parser_service.parse_excel_file(buffer, "test.txt")

        assert result.success is False
        assert "Formato de arquivo não suportado" in result.errors[0]

    @pytest.mark.asyncio
    async def test_parse_file_with_different_datetime_formats(
        self, parser_service: ExcelParserService
    ):
        """Test parsing file with different datetime formats."""
        data = {
            "Nome da Marca": ["Clínica A", "Clínica B", "Clínica C"],
            "Nome da Unidade": ["UBS Centro", "UBS Norte", "UBS Sul"],
            "Nome do Paciente": ["João Silva", "Maria Santos", "Pedro Costa"],
            "Data/Hora Início Agendamento": [
                "15/01/2025 14:30",
                "16/01/2025 10:00:00",
                datetime(2025, 1, 17, 16, 45),
            ],
            "Status Agendamento": ["Confirmado", "Confirmado", "Confirmado"],
            "Contato(s) do Paciente": [
                "11999887766",
                "11988776655",
                "11977665544",
            ],
            "Observação": ["OK", "OK", "OK"],
            "Nomes dos Exames": [
                "Clínico Geral",
                "Cardiologia",
                "Dermatologia",
            ],
        }

        excel_file = self.create_excel_file(data)

        result = await parser_service.parse_excel_file(excel_file, "test.xlsx")

        assert result.success is True
        assert result.total_rows == 3
        assert result.valid_rows == 3
        assert len(result.appointments) == 3

        # Check that all datetime formats were parsed correctly
        appointments = result.appointments
        assert appointments[0].data_agendamento == datetime(2025, 1, 15)
        assert appointments[1].data_agendamento == datetime(2025, 1, 16)
        assert appointments[2].data_agendamento == datetime(2025, 1, 17)

        assert appointments[0].hora_agendamento == "14:30"
        assert appointments[1].hora_agendamento == "10:00"
        assert appointments[2].hora_agendamento == "16:45"
