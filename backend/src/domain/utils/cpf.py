"""CPF utilities for normalization and validation helpers."""

import re
from typing import Optional


def normalize_cpf(cpf: Optional[str]) -> Optional[str]:
    """Return CPF digits only, preserving None values."""

    if cpf is None:
        return None

    digits = re.sub(r"\D", "", cpf)
    return digits or None


def is_valid_cpf(cpf: Optional[str]) -> bool:
    """Validate CPF format and verification digits."""

    normalized = normalize_cpf(cpf)
    if normalized is None:
        return False

    if len(normalized) != 11:
        return False

    if normalized == normalized[0] * 11:
        return False

    digits = [int(char) for char in normalized]

    sum1 = sum(digits[i] * (10 - i) for i in range(9))
    remainder1 = sum1 % 11
    expected_first = 0 if remainder1 < 2 else 11 - remainder1
    if digits[9] != expected_first:
        return False

    sum2 = sum(digits[i] * (11 - i) for i in range(10))
    remainder2 = sum2 % 11
    expected_second = 0 if remainder2 < 2 else 11 - remainder2
    return digits[10] == expected_second
