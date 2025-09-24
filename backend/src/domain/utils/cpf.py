"""CPF utilities for normalization and validation helpers."""

import re
from typing import Optional


def normalize_cpf(cpf: Optional[str]) -> Optional[str]:
    """Return CPF digits only, preserving None values.

    Args:
        cpf: CPF value possibly containing formatting characters.

    Returns:
        Normalized CPF with only numbers or None when no value was provided.
    """
    if cpf is None:
        return None

    digits = re.sub(r"\D", "", cpf)
    return digits or None
