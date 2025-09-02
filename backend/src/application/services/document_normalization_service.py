"""
Service for normalizing CPF and RG documents using OpenRouter's openai/gpt-oss-20b:free model.
"""

import json
import logging
import os
import re
from typing import Dict, Optional

from openai import OpenAI
from pydantic import BaseModel

from src.infrastructure.config import get_settings

logger = logging.getLogger(__name__)


class NormalizedDocuments(BaseModel):
    """Structure for normalized document components."""

    cpf: Optional[str] = None
    rg: Optional[str] = None
    cpf_formatted: Optional[str] = None
    rg_formatted: Optional[str] = None


class DocumentNormalizationService:
    """
    Service for normalizing Brazilian CPF and RG documents using OpenRouter AI.

    This service takes unstructured document strings and extracts CPF and RG
    information using the "openai/gpt-oss-20b:free" model.
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

    async def normalize_documents(
        self, documento_completo: str
    ) -> Optional[Dict[str, Optional[str]]]:
        """
        Normalize a document string into structured CPF and RG components.

        Args:
            documento_completo: Document string like "CPF: 12345678901, RG: 123456789"

        Returns:
            Dictionary with normalized document components or None if normalization fails
        """
        # Check if document normalization is disabled
        settings = get_settings()
        if (
            not settings.address_normalization_enabled
        ):  # Reuse the same setting
            logger.info("Document normalization is disabled, skipping...")
            return None

        if not documento_completo or not documento_completo.strip():
            return None

        try:
            # Create prompt for document normalization
            prompt = self._create_normalization_prompt(documento_completo)

            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em normalização de documentos brasileiros (CPF e RG). "
                        "IMPORTANTE: Você DEVE responder APENAS com JSON válido, sem texto adicional.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=300,
                top_p=0.9,
            )

            # Parse response
            result_text = response.choices[0].message.content.strip()
            logger.info(
                f"OpenRouter response for documents '{documento_completo}': {result_text}"
            )

            # Extract JSON from response
            normalized = self._parse_response(result_text)

            if normalized:
                # Validate the normalized documents
                return self._validate_normalized_documents(normalized)

            return None

        except Exception as e:
            logger.error(
                f"Error normalizing documents '{documento_completo}': {str(e)}"
            )
            return None

    def _create_normalization_prompt(self, documento_completo: str) -> str:
        """Create the prompt for document normalization."""
        return f"""
Analise a seguinte string de documentos brasileiros e extraia as informações em formato JSON:

Documentos: "{documento_completo}"

Extraia e normalize os seguintes campos:
- cpf: Apenas os 11 dígitos do CPF (sem pontos, traços ou espaços)
- rg: Apenas os dígitos do RG (sem pontos, traços ou espaços)  
- cpf_formatted: CPF formatado como XXX.XXX.XXX-XX (se válido)
- rg_formatted: RG formatado com pontos se necessário (se válido)

Regras importantes:
1. CPF deve ter exatamente 11 dígitos
2. RG pode ter de 7 a 9 dígitos
3. Ignore prefixos como "CPF:", "RG:", espaços e formatação
4. Se houver múltiplos RGs, use o primeiro válido
5. Valide se os números fazem sentido (não devem ser todos iguais)
6. Se não conseguir identificar algum documento, use null
7. Aplique validação básica de CPF (dígito verificador)

Exemplos de entrada e saída:
- "CPF: 12345678901, RG: 123456789" → cpf: "12345678901", rg: "123456789"
- "RG: 123456789, CPF: 12345678901" → cpf: "12345678901", rg: "123456789" 
- "CPF: 12345678901" → cpf: "12345678901", rg: null

Responda APENAS com o JSON válido, sem texto adicional:

{{
  "cpf": "...",
  "rg": "...",
  "cpf_formatted": "...",
  "rg_formatted": "..."
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

    def _validate_normalized_documents(
        self, normalized: Dict
    ) -> Optional[Dict[str, Optional[str]]]:
        """Validate and clean the normalized documents."""
        try:
            # Extract and validate CPF
            cpf = self._clean_document(normalized.get("cpf"))
            rg = self._clean_document(normalized.get("rg"))

            # Validate CPF format and checksum
            if cpf and not self._is_valid_cpf(cpf):
                logger.warning(f"Invalid CPF format or checksum: {cpf}")
                cpf = None

            # Validate RG format
            if rg and not self._is_valid_rg(rg):
                logger.warning(f"Invalid RG format: {rg}")
                rg = None

            # If we don't have at least one valid document, return None
            if not cpf and not rg:
                return None

            # Create formatted versions
            cpf_formatted = self._format_cpf(cpf) if cpf else None
            rg_formatted = self._format_rg(rg) if rg else None

            result = {
                "cpf": cpf,
                "rg": rg,
                "cpf_formatted": cpf_formatted,
                "rg_formatted": rg_formatted,
            }

            return result

        except Exception as e:
            logger.error(f"Error validating normalized documents: {e}")
            return None

    def _clean_document(self, value) -> Optional[str]:
        """Clean and validate document fields."""
        if not value or value == "null":
            return None

        # Remove all non-digit characters
        cleaned = re.sub(r"\D", "", str(value).strip())
        return cleaned if cleaned else None

    def _is_valid_cpf(self, cpf: str) -> bool:
        """Validate CPF using Brazilian algorithm."""
        if not cpf or len(cpf) != 11:
            return False

        # Check for obvious invalid patterns (all same digits)
        if cpf == cpf[0] * 11:
            return False

        # Validate checksum digits
        try:
            # Calculate first digit
            sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
            digit1 = 11 - (sum1 % 11)
            if digit1 >= 10:
                digit1 = 0

            # Calculate second digit
            sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
            digit2 = 11 - (sum2 % 11)
            if digit2 >= 10:
                digit2 = 0

            # Check if calculated digits match
            return int(cpf[9]) == digit1 and int(cpf[10]) == digit2

        except (ValueError, IndexError):
            return False

    def _is_valid_rg(self, rg: str) -> bool:
        """Validate RG format."""
        if not rg:
            return False

        # RG should have 7-9 digits
        return 7 <= len(rg) <= 9 and rg.isdigit()

    def _format_cpf(self, cpf: str) -> str:
        """Format CPF as XXX.XXX.XXX-XX."""
        if not cpf or len(cpf) != 11:
            return cpf

        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    def _format_rg(self, rg: str) -> str:
        """Format RG with dots if needed."""
        if not rg:
            return rg

        # Most common RG format in Brazil: XX.XXX.XXX for 8-digit RG
        if len(rg) == 8:
            return f"{rg[:2]}.{rg[2:5]}.{rg[5:]}"
        elif len(rg) == 9:
            # 9-digit RG: XXX.XXX.XXX
            return f"{rg[:3]}.{rg[3:6]}.{rg[6:]}"
        else:
            return rg  # Return as-is for other lengths

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
