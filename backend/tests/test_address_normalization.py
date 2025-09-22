"""
Tests for address normalization service.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.application.services.address_normalization_service import (
    AddressNormalizationService,
)


class TestAddressNormalizationService:
    """Test suite for AddressNormalizationService."""

    def test_init_with_api_key(self):
        """Test service initialization with API key."""
        with patch.dict("os.environ", {}, clear=True):
            service = AddressNormalizationService(api_key="test-key")
            assert service.api_key == "test-key"
            assert service.model == "openai/gpt-oss-20b:free"

    def test_init_without_api_key_raises_error(self):
        """Test service initialization without API key raises error."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(
                ValueError, match="OpenRouter API key not provided"
            ):
                AddressNormalizationService()

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "env-test-key"})
    def test_init_with_env_var(self):
        """Test service initialization with environment variable."""
        service = AddressNormalizationService()
        assert service.api_key == "env-test-key"

    @pytest.mark.asyncio
    async def test_normalize_address_success(self):
        """Test successful address normalization."""
        # Mock OpenRouter response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = """
        {
          "rua": "Rua Maurício da Costa Faria",
          "numero": "52",
          "complemento": null,
          "bairro": "Recreio dos Bandeirantes",
          "cidade": "Rio de Janeiro",
          "estado": "RJ",
          "cep": "22790-285"
        }
        """

        with patch(
            "src.application.services.address_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            service = AddressNormalizationService(api_key="test-key")
            result = await service.normalize_address(
                "rua maurício da costa faria,52,recreio dos bandeirantes,rio de janeiro,RJ,22790-285"
            )

            assert result is not None
            assert result["rua"] == "Rua Maurício da Costa Faria"
            assert result["numero"] == "52"
            assert result["complemento"] is None
            assert result["bairro"] == "Recreio dos Bandeirantes"
            assert result["cidade"] == "Rio de Janeiro"
            assert result["estado"] == "RJ"
            assert result["cep"] == "22790-285"

    @pytest.mark.asyncio
    async def test_normalize_address_empty_input(self):
        """Test normalization with empty input."""
        service = AddressNormalizationService(api_key="test-key")
        result = await service.normalize_address("")
        assert result is None

        result = await service.normalize_address(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_normalize_address_invalid_json_response(self):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Invalid JSON response"

        with patch(
            "src.application.services.address_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            service = AddressNormalizationService(api_key="test-key")
            result = await service.normalize_address("some address")

            assert result is None

    @pytest.mark.asyncio
    async def test_normalize_address_openrouter_api_error(self):
        """Test handling of OpenRouter API errors."""
        with patch(
            "src.application.services.address_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception(
                "API Error"
            )
            mock_openai.return_value = mock_client

            service = AddressNormalizationService(api_key="test-key")
            result = await service.normalize_address("some address")

            assert result is None

    @pytest.mark.asyncio
    async def test_normalize_address_missing_required_fields(self):
        """Test normalization with response missing required fields."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = """
        {
          "numero": "52",
          "bairro": "Recreio dos Bandeirantes"
        }
        """

        with patch(
            "src.application.services.address_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            service = AddressNormalizationService(api_key="test-key")
            result = await service.normalize_address("incomplete address")

            assert result is None

    def test_clean_string(self):
        """Test string cleaning method."""
        service = AddressNormalizationService(api_key="test-key")

        assert service._clean_string("  test  ") == "test"
        assert service._clean_string("") is None
        assert service._clean_string("null") is None
        assert service._clean_string(None) is None
        assert service._clean_string("valid string") == "valid string"

    def test_clean_cep(self):
        """Test CEP cleaning and formatting."""
        service = AddressNormalizationService(api_key="test-key")

        assert service._clean_cep("22790285") == "22790-285"
        assert service._clean_cep("22790-285") == "22790-285"
        assert service._clean_cep("227902851") is None  # Too many digits
        assert service._clean_cep("2279028") is None  # Too few digits
        assert service._clean_cep("") is None
        assert service._clean_cep(None) is None
        assert service._clean_cep("null") is None

    def test_create_normalization_prompt(self):
        """Test prompt creation for OpenRouter."""
        service = AddressNormalizationService(api_key="test-key")

        endereco = "rua maurício da costa faria,52,recreio dos bandeirantes,rio de janeiro,RJ,22790-285"
        prompt = service._create_normalization_prompt(endereco)

        assert endereco in prompt
        assert "JSON" in prompt
        assert "rua" in prompt
        assert "numero" in prompt
        assert "bairro" in prompt
        assert "cidade" in prompt
        assert "estado" in prompt
        assert "cep" in prompt

    def test_validate_normalized_address_success(self):
        """Test successful address validation."""
        service = AddressNormalizationService(api_key="test-key")

        normalized = {
            "rua": "Rua Maurício da Costa Faria",
            "numero": "52",
            "complemento": None,
            "bairro": "Recreio dos Bandeirantes",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "cep": "22790-285",
        }

        result = service._validate_normalized_address(normalized)

        assert result is not None
        assert result["rua"] == "Rua Maurício da Costa Faria"
        assert result["numero"] == "52"
        assert result["complemento"] is None
        assert result["bairro"] == "Recreio dos Bandeirantes"
        assert result["cidade"] == "Rio de Janeiro"
        assert result["estado"] == "RJ"
        assert result["cep"] == "22790-285"

    def test_validate_normalized_address_missing_required(self):
        """Test address validation with missing required fields."""
        service = AddressNormalizationService(api_key="test-key")

        # Missing rua
        normalized = {
            "numero": "52",
            "bairro": "Recreio dos Bandeirantes",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "cep": "22790-285",
        }

        result = service._validate_normalized_address(normalized)
        assert result is None

    def test_validate_normalized_address_invalid_estado(self):
        """Test address validation with invalid estado format."""
        service = AddressNormalizationService(api_key="test-key")

        normalized = {
            "rua": "Rua Maurício da Costa Faria",
            "numero": "52",
            "bairro": "Recreio dos Bandeirantes",
            "cidade": "Rio de Janeiro",
            "estado": "Rio de Janeiro",  # Should be "RJ"
            "cep": "22790-285",
        }

        result = service._validate_normalized_address(normalized)

        assert result is not None
        assert result["estado"] == "RI"  # Should be truncated to 2 characters

    def test_parse_response_success(self):
        """Test successful response parsing."""
        service = AddressNormalizationService(api_key="test-key")

        response_text = """Some text before
        {
          "rua": "Rua Test",
          "numero": "123"
        }
        Some text after"""

        result = service._parse_response(response_text)

        assert result is not None
        assert result["rua"] == "Rua Test"
        assert result["numero"] == "123"

    def test_parse_response_no_json(self):
        """Test response parsing when no JSON is found."""
        service = AddressNormalizationService(api_key="test-key")

        response_text = "No JSON here at all"
        result = service._parse_response(response_text)

        assert result is None

    def test_parse_response_invalid_json(self):
        """Test response parsing with invalid JSON."""
        service = AddressNormalizationService(api_key="test-key")

        response_text = "{ invalid json }"
        result = service._parse_response(response_text)

        assert result is None

    def test_is_service_available_success(self):
        """Test service availability check - success."""
        mock_response = MagicMock()

        with patch(
            "src.application.services.address_normalization_service.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            service = AddressNormalizationService(api_key="test-key")
            assert service.is_service_available() is True

    def test_is_service_available_failure(self):
        """Test service availability check - failure."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception(
                "API Error"
            )
            mock_openai.return_value = mock_client

            service = AddressNormalizationService(api_key="test-key")
            assert service.is_service_available() is False


@pytest.mark.integration
class TestAddressNormalizationIntegration:
    """Integration tests for address normalization service."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires actual OpenRouter API key")
    async def test_real_address_normalization(self):
        """Test with real OpenRouter API (requires API key)."""
        # This test is skipped by default as it requires a real API key
        # Uncomment and provide a valid API key to run

        # service = AddressNormalizationService(api_key="your-real-api-key")
        # result = await service.normalize_address(
        #     "rua maurício da costa faria,52,recreio dos bandeirantes,rio de janeiro,RJ,22790-285"
        # )
        #
        # assert result is not None
        # assert "rua" in result
        # assert "numero" in result
        # assert "cidade" in result
        pass
