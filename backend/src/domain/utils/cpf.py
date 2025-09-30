"""CPF utilities for normalization, formatting and validation helpers."""

from __future__ import annotations

import re
from typing import Optional

__all__ = ["normalize_cpf", "is_valid_cpf", "format_cpf"]


def normalize_cpf(cpf: Optional[str]) -> Optional[str]:
    """Return CPF digits only, preserving ``None`` values.

    Args:
        cpf: CPF value possibly containing formatting characters.

    Returns:
        Normalized CPF with only numbers or ``None`` when no value was provided.
    """
    if cpf is None:
        return None

    digits = re.sub(r"\D", "", cpf)
    return digits or None


def is_valid_cpf(cpf: Optional[str]) -> bool:
    """Validate CPF digits using the official checksum algorithm."""

    digits = normalize_cpf(cpf)
    if digits is None or len(digits) != 11:
        return False

    if digits == digits[0] * len(digits):
        return False

    for check_position in (9, 10):
        total = 0
        for index in range(check_position):
            weight = (check_position + 1) - index
            total += int(digits[index]) * weight

        remainder = (total * 10) % 11
        if remainder == 10:
            remainder = 0

        if remainder != int(digits[check_position]):
            return False

    return True


def format_cpf(cpf: Optional[str]) -> Optional[str]:
    """Return a formatted CPF (XXX.XXX.XXX-XX) when possible."""

    digits = normalize_cpf(cpf)
    if digits is None or len(digits) != 11:
        return None

    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
