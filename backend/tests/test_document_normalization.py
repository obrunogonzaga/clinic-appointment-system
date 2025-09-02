"""
Tests for document normalization service.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.application.services.document_normalization_service import (
    DocumentNormalizationService,
)


class TestDocumentNormalizationService:
    """Test cases for DocumentNormalizationService."""

    def test_init_with_api_key(self):
        """Test service initialization with API key."""
        service = DocumentNormalizationService(api_key="test-key")
        assert service.api_key == "test-key"

    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(
                ValueError, match="OpenRouter API key not provided"
            ):
                DocumentNormalizationService()

    def test_init_with_env_var(self):
        """Test service initialization using environment variable."""
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "env-test-key"}):
            service = DocumentNormalizationService()
            assert service.api_key == "env-test-key"

    @pytest.mark.asyncio
    async def test_normalize_documents_success(self):
        """Test successful document normalization."""
        # Mock OpenRouter response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = """
        {
            "cpf": "11144477735",
            "rg": "123456789",
            "cpf_formatted": "111.444.777-35",
            "rg_formatted": "123.456.789"
        }
        """

        with patch(
            "src.application.services.document_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            service = DocumentNormalizationService(api_key="test-key")
            result = await service.normalize_documents(
                "CPF: 11144477735, RG: 123456789"
            )

            assert result is not None
            assert result["cpf"] == "11144477735"
            assert result["rg"] == "123456789"
            assert result["cpf_formatted"] == "111.444.777-35"
            assert result["rg_formatted"] == "123.456.789"

    @pytest.mark.asyncio
    async def test_normalize_documents_empty_input(self):
        """Test normalization with empty input."""
        service = DocumentNormalizationService(api_key="test-key")
        result = await service.normalize_documents("")
        assert result is None

        result = await service.normalize_documents(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_normalize_documents_invalid_json_response(self):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Invalid JSON content"

        with patch(
            "src.application.services.document_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            service = DocumentNormalizationService(api_key="test-key")
            result = await service.normalize_documents("CPF: 12345678901")

            assert result is None

    @pytest.mark.asyncio
    async def test_normalize_documents_openrouter_api_error(self):
        """Test handling of OpenRouter API errors."""
        with patch(
            "src.application.services.document_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception(
                "API Error"
            )
            mock_openai.return_value = mock_client

            service = DocumentNormalizationService(api_key="test-key")
            result = await service.normalize_documents("CPF: 12345678901")

            assert result is None

    @pytest.mark.asyncio
    async def test_normalize_documents_invalid_cpf(self):
        """Test normalization with invalid CPF."""
        # Mock response with invalid CPF
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = """
        {
            "cpf": "11111111111",
            "rg": "123456789",
            "cpf_formatted": "111.111.111-11",
            "rg_formatted": "123.456.789"
        }
        """

        with patch(
            "src.application.services.document_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            service = DocumentNormalizationService(api_key="test-key")
            result = await service.normalize_documents(
                "CPF: 11111111111, RG: 123456789"
            )

            # Should return result with RG only since CPF is invalid
            assert result is not None
            assert result["cpf"] is None
            assert result["rg"] == "123456789"
            assert result["cpf_formatted"] is None
            assert result["rg_formatted"] == "123.456.789"

    @pytest.mark.asyncio
    async def test_normalize_documents_only_cpf(self):
        """Test normalization with only CPF."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = """
        {
            "cpf": "11144477735",
            "rg": null,
            "cpf_formatted": "111.444.777-35",
            "rg_formatted": null
        }
        """

        with patch(
            "src.application.services.document_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            service = DocumentNormalizationService(api_key="test-key")
            result = await service.normalize_documents("CPF: 11144477735")

            assert result is not None
            assert result["cpf"] == "11144477735"
            assert result["rg"] is None
            assert result["cpf_formatted"] == "111.444.777-35"
            assert result["rg_formatted"] is None

    @pytest.mark.asyncio
    async def test_normalize_documents_only_rg(self):
        """Test normalization with only RG."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = """
        {
            "cpf": null,
            "rg": "123456789",
            "cpf_formatted": null,
            "rg_formatted": "123.456.789"
        }
        """

        with patch(
            "src.application.services.document_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            service = DocumentNormalizationService(api_key="test-key")
            result = await service.normalize_documents("RG: 123456789")

            assert result is not None
            assert result["cpf"] is None
            assert result["rg"] == "123456789"
            assert result["cpf_formatted"] is None
            assert result["rg_formatted"] == "123.456.789"

    def test_is_valid_cpf_valid(self):
        """Test CPF validation with valid CPFs."""
        service = DocumentNormalizationService(api_key="test-key")

        # Valid CPF examples
        assert service._is_valid_cpf("11144477735")  # Example valid CPF
        assert service._is_valid_cpf("01234567890")  # Another valid CPF

    def test_is_valid_cpf_invalid(self):
        """Test CPF validation with invalid CPFs."""
        service = DocumentNormalizationService(api_key="test-key")

        # Invalid CPF examples
        assert not service._is_valid_cpf("11111111111")  # All same digits
        assert not service._is_valid_cpf("12345678901")  # Invalid checksum
        assert not service._is_valid_cpf("123456789")  # Wrong length
        assert not service._is_valid_cpf("")  # Empty string
        assert not service._is_valid_cpf(None)  # None

    def test_is_valid_rg_valid(self):
        """Test RG validation with valid RGs."""
        service = DocumentNormalizationService(api_key="test-key")

        assert service._is_valid_rg("1234567")  # 7 digits
        assert service._is_valid_rg("12345678")  # 8 digits
        assert service._is_valid_rg("123456789")  # 9 digits

    def test_is_valid_rg_invalid(self):
        """Test RG validation with invalid RGs."""
        service = DocumentNormalizationService(api_key="test-key")

        assert not service._is_valid_rg("123456")  # Too short
        assert not service._is_valid_rg("1234567890")  # Too long
        assert not service._is_valid_rg("12345a67")  # Contains letter
        assert not service._is_valid_rg("")  # Empty string
        assert not service._is_valid_rg(None)  # None

    def test_format_cpf(self):
        """Test CPF formatting."""
        service = DocumentNormalizationService(api_key="test-key")

        assert service._format_cpf("12345678901") == "123.456.789-01"
        assert service._format_cpf("") == ""
        assert (
            service._format_cpf("123456789") == "123456789"
        )  # Invalid length, return as-is

    def test_format_rg(self):
        """Test RG formatting."""
        service = DocumentNormalizationService(api_key="test-key")

        assert service._format_rg("12345678") == "12.345.678"
        assert service._format_rg("123456789") == "123.456.789"
        assert (
            service._format_rg("1234567") == "1234567"
        )  # 7 digits, return as-is
        assert service._format_rg("") == ""

    def test_clean_document(self):
        """Test document cleaning."""
        service = DocumentNormalizationService(api_key="test-key")

        assert service._clean_document("123.456.789-01") == "12345678901"
        assert service._clean_document("12.345.678") == "12345678"
        assert service._clean_document("CPF: 123.456.789-01") == "12345678901"
        assert service._clean_document("null") is None
        assert service._clean_document("") is None
        assert service._clean_document(None) is None

    @pytest.mark.asyncio
    async def test_normalize_documents_disabled_setting(self):
        """Test normalization with disabled setting."""
        with patch(
            "src.application.services.document_normalization_service.get_settings"
        ) as mock_settings:
            mock_settings.return_value.address_normalization_enabled = False

            service = DocumentNormalizationService(api_key="test-key")
            result = await service.normalize_documents("CPF: 12345678901")

            assert result is None

    @pytest.mark.asyncio
    async def test_normalize_documents_rg_first_order(self):
        """Test normalization with RG first in the string."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = """
        {
            "cpf": "11144477735",
            "rg": "123456789",
            "cpf_formatted": "111.444.777-35", 
            "rg_formatted": "123.456.789"
        }
        """

        with patch(
            "src.application.services.document_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            service = DocumentNormalizationService(api_key="test-key")
            result = await service.normalize_documents(
                "RG: 123456789, CPF: 11144477735"
            )

            assert result is not None
            assert result["cpf"] == "11144477735"
            assert result["rg"] == "123456789"

    def test_service_availability_check(self):
        """Test service availability check."""
        with patch(
            "src.application.services.document_normalization_service.OpenAI"
        ) as mock_openai:
            # Test successful availability check
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = MagicMock()
            mock_openai.return_value = mock_client

            service = DocumentNormalizationService(api_key="test-key")
            assert service.is_service_available() == True

            # Test failed availability check
            mock_client.chat.completions.create.side_effect = Exception(
                "Service unavailable"
            )
            assert service.is_service_available() == False

    @pytest.mark.asyncio
    async def test_integration_real_scenarios(self):
        """Test with real-world document patterns from Excel."""
        real_patterns = [
            "CPF: 09296806771, RG: 339396194",
            "CPF: 39581799753, RG: 856053962",
            "CPF: 06911008700",
            "RG: 218818482, CPF: 11409945731",
            "CPF: 03541623730, RG: 099650566",
            "RG: 056189699, RG: 0056189699, CPF: 72730293787",
        ]

        for pattern in real_patterns:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[
                0
            ].message.content = """
            {
                "cpf": "11144477735",
                "rg": "123456789",
                "cpf_formatted": "111.444.777-35",
                "rg_formatted": "123.456.789"
            }
            """

            with patch(
                "src.application.services.document_normalization_service.OpenAI"
            ) as mock_openai:
                mock_client = MagicMock()
                mock_client.chat.completions.create.return_value = (
                    mock_response
                )
                mock_openai.return_value = mock_client

                service = DocumentNormalizationService(api_key="test-key")
                result = await service.normalize_documents(pattern)

                # Should not throw exceptions and should return a result
                assert result is not None
                assert "cpf" in result
                assert "rg" in result

    # Uncomment for manual integration testing with real API
    # @pytest.mark.skip(reason="Integration test - requires real API key")
    # @pytest.mark.asyncio
    # async def test_real_api_integration(self):
    #     """Integration test with real OpenRouter API."""
    #     # Uncomment and provide a valid API key to run
    #
    #     # service = DocumentNormalizationService(api_key="your-real-api-key")
    #     # result = await service.normalize_documents(
    #     #     "CPF: 12345678901, RG: 123456789"
    #     # )
    #     #
    #     # print("Real API result:", result)
    #     # assert result is not None
