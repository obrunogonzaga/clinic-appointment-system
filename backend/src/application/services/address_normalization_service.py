"""
Service for normalizing addresses using OpenRouter's openai/gpt-oss-20b:free model.
"""

import json
import logging
import os
from typing import Dict, Optional

from openai import OpenAI
from pydantic import BaseModel

from src.infrastructure.config import get_settings

logger = logging.getLogger(__name__)


class NormalizedAddress(BaseModel):
    """Structure for normalized address components."""

    rua: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    cep: str


class AddressNormalizationService:
    """
    Service for normalizing Brazilian addresses using OpenRouter AI.

    This service takes unstructured address strings and breaks them down
    into structured components using the "openai/gpt-oss-20b:free" model.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the service with OpenRouter credentials.

        Args:
            api_key: OpenRouter API key. If None, will try to get from OPENROUTER_API_KEY env var.
            model: OpenRouter model name. If None, will try to get from OPENROUTER_MODEL env var.
            base_url: OpenRouter base URL. If None, will try to get from OPENROUTER_BASE_URL env var.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not provided. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.base_url = base_url or os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model = model or os.getenv(
            "OPENROUTER_MODEL", "openai/gpt-oss-20b:free"
        )

    async def normalize_address(
        self, endereco_completo: str
    ) -> Optional[Dict[str, Optional[str]]]:
        """
        Normalize a complete address string into structured components.

        Args:
            endereco_completo: Full address string like "rua maurício da costa faria,52,recreio dos bandeirantes,rio de janeiro,RJ,22790-285"

        Returns:
            Dictionary with normalized address components or None if normalization fails
        """
        # Check if address normalization is disabled
        settings = get_settings()
        if not settings.address_normalization_enabled:
            logger.info("Address normalization is disabled, skipping...")
            return None

        if not endereco_completo or not endereco_completo.strip():
            return None

        try:
            # Create prompt for address normalization
            prompt = self._create_normalization_prompt(endereco_completo)

            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em normalização de endereços brasileiros. "
                        "IMPORTANTE: Você DEVE responder APENAS com JSON válido, sem texto adicional.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=500,
                top_p=0.9,
            )

            # Parse response
            result_text = response.choices[0].message.content.strip()
            logger.info(
                f"OpenRouter response for address '{endereco_completo}': {result_text}"
            )

            # Extract JSON from response
            normalized = self._parse_response(result_text)

            if normalized:
                # Validate the normalized address
                return self._validate_normalized_address(normalized)

            return None

        except Exception as e:
            logger.error(
                f"Error normalizing address '{endereco_completo}': {str(e)}"
            )
            return None

    def _create_normalization_prompt(self, endereco_completo: str) -> str:
        """Create the prompt for address normalization."""
        return f"""
Analise o seguinte endereço brasileiro não estruturado e extraia as informações em formato JSON:

Endereço: "{endereco_completo}"

Extraia e normalize os seguintes campos:
- rua: Nome da rua (com tipo como "Rua", "Avenida", etc.)
- numero: Número do imóvel (apenas números)
- complemento: Apartamento, bloco, sala, etc. (se houver)
- bairro: Nome do bairro
- cidade: Nome da cidade
- estado: Sigla do estado (2 letras maiúsculas)
- cep: CEP formatado com hífen (XXXXX-XXX)

Regras importantes:
1. Se o tipo da rua não estiver explícito, adicione "Rua" no início
2. Capitalize nomes próprios (primeira letra maiúscula)
3. Mantenha apenas números no campo "numero"
4. Se não conseguir identificar algum campo, use null
5. CEP deve ter formato XXXXX-XXX (5 dígitos + hífen + 3 dígitos)

Responda APENAS com o JSON válido, sem texto adicional:

{{
  "rua": "...",
  "numero": "...",
  "complemento": null,
  "bairro": "...",
  "cidade": "...",
  "estado": "...",
  "cep": "..."
}}
"""

    def _parse_response(self, response_text: str) -> Optional[Dict]:
        """Parse the JSON response from OpenRouter."""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                logger.warning(f"No JSON found in response: {response_text}")
                return None

            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Response text: {response_text}")
            return None
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return None

    def _validate_normalized_address(
        self, normalized: Dict
    ) -> Optional[Dict[str, Optional[str]]]:
        """Validate and clean the normalized address."""
        try:
            # Check if we have the minimum required information
            if not all(
                normalized.get(field) for field in ["rua", "cidade", "estado"]
            ):
                logger.warning(
                    f"Missing required fields in normalized address: {normalized}"
                )
                return None

            # Create validated structure
            result = {
                "rua": self._clean_string(normalized.get("rua")),
                "numero": self._clean_string(normalized.get("numero")),
                "complemento": self._clean_string(
                    normalized.get("complemento")
                ),
                "bairro": self._clean_string(normalized.get("bairro")),
                "cidade": self._clean_string(normalized.get("cidade")),
                "estado": self._clean_string(normalized.get("estado")),
                "cep": self._clean_cep(normalized.get("cep")),
            }

            # Validate estado (should be 2 letters)
            if result["estado"] and len(result["estado"]) != 2:
                logger.warning(f"Invalid estado format: {result['estado']}")
                result["estado"] = (
                    result["estado"][:2].upper() if result["estado"] else None
                )

            return result

        except Exception as e:
            logger.error(f"Error validating normalized address: {e}")
            return None

    def _clean_string(self, value) -> Optional[str]:
        """Clean and validate string fields."""
        if not value or value == "null":
            return None

        cleaned = str(value).strip()
        return cleaned if cleaned else None

    def _clean_cep(self, cep) -> Optional[str]:
        """Clean and format CEP."""
        if not cep or cep == "null":
            return None

        # Remove any non-digit characters
        digits_only = "".join(filter(str.isdigit, str(cep)))

        # CEP should have exactly 8 digits
        if len(digits_only) != 8:
            return None

        # Format as XXXXX-XXX
        return f"{digits_only[:5]}-{digits_only[5:]}"

    def is_service_available(self) -> bool:
        """Check if the OpenRouter service is available."""
        try:
            # Simple test call
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
            )
            return True
        except Exception as e:
            logger.error(f"OpenRouter service not available: {e}")
            return False
