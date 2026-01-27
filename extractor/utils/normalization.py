from __future__ import annotations

import re
from datetime import datetime
from typing import Optional, Tuple

MONTH_MAP = {
    "JAN": "01",
    "FEV": "02",
    "MAR": "03",
    "ABR": "04",
    "MAI": "05",
    "JUN": "06",
    "JUL": "07",
    "AGO": "08",
    "SET": "09",
    "OUT": "10",
    "NOV": "11",
    "DEZ": "12",
}

ASSET_TYPE_MAP = {
    "CDB": "Renda Fixa",
    "LCI": "Renda Fixa",
    "LCA": "Renda Fixa",
    "LIG": "Renda Fixa",
    "CRI": "Renda Fixa",
    "CRA": "Renda Fixa",
    "DEB": "Renda Fixa",
    "NTN-B": "Renda Fixa",
    "NTN-F": "Renda Fixa",
    "LFT": "Renda Fixa",
    "LTN": "Renda Fixa",
    "TESOURO PREFIXADO": "Renda Fixa",
    "FII": "Fii",
    "Fundo Multimercado": "Fundos de Investimento",
    "Ação": "Ação",
    "FGTS": "Fundos de Investimento",
    "Previdência": "Fundos de Previdência",
}

INDEXER_PATTERNS = [
    (re.compile(r"CDI", re.IGNORECASE), "CDI"),
    (re.compile(r"IPCA|IPC-A", re.IGNORECASE), "IPC-A"),
    (re.compile(r"SELIC|LFT", re.IGNORECASE), "SELIC"),
    (re.compile(r"PR[ÉE]|PREFIXADO|PRE", re.IGNORECASE), "PRE"),
]

RATE_PATTERNS = [
    re.compile(r"CDI\s*\+?\s*([\d.,]+)%", re.IGNORECASE),
    re.compile(r"(?:IPCA|IPC-A)\s*\+?\s*([\d.,]+)%", re.IGNORECASE),
    re.compile(r"(?:PR[ÉE]|PRE|Prefixado)\s*([\d.,]+)%", re.IGNORECASE),
    re.compile(r"([\d.,]+)%\s*a\.a\.", re.IGNORECASE),
]

DATE_PATTERN = re.compile(r"(\d{2})/(\d{2})/(\d{4})")
MONTH_YEAR_PATTERN = re.compile(r"(\d{2})/(\d{4})")


def normalize_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value


def _normalize_decimal_string(value: str) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    elif value.count(".") == 1:
        # already in english decimal format
        pass
    else:
        value = value.replace(".", "")
    value = re.sub(r"[^0-9\.-]", "", value)
    return value or None


def normalize_decimal(value: object) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = _normalize_decimal_string(str(value))
    return float(cleaned) if cleaned is not None and cleaned not in {"", "-"} else None


def normalize_money(value: object) -> Optional[float]:
    return normalize_decimal(value)


def ensure_iso_date(value: object) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        # already ISO
        try:
            return datetime.fromisoformat(value).date().isoformat()
        except ValueError:
            pass
        parsed = parse_date(value)
        if parsed:
            return parsed
    return None


def parse_date(text: str, default_day: int = 1) -> Optional[str]:
    text = text.strip()
    match = DATE_PATTERN.search(text)
    if match:
        day, month, year = match.groups()
        return datetime(int(year), int(month), int(day)).date().isoformat()

    # Month name e.g. MAI/2027
    month_name_match = re.search(r"([A-ZÇ]{3})\/?(\d{4})", text, re.IGNORECASE)
    if month_name_match:
        month_text, year = month_name_match.groups()
        month_key = month_text.upper()[:3]
        month = MONTH_MAP.get(month_key)
        if month:
            return datetime(int(year), int(month), default_day).date().isoformat()

    month_year = MONTH_YEAR_PATTERN.search(text)
    if month_year:
        month, year = month_year.groups()
        return datetime(int(year), int(month), default_day).date().isoformat()

    return None


def classify_asset(name: str) -> Tuple[Optional[str], Optional[str]]:
    name = normalize_text(name).upper()
    if not name:
        return None, None

    mappings = [
        (r"CDB", "CDB"),
        (r"LCI", "LCI"),
        (r"LCA", "LCA"),
        (r"LIG", "LIG"),
        (r"CRI", "CRI"),
        (r"CRA", "CRA"),
        (r"DEB", "DEB"),
        (r"NTN-B", "NTN-B"),
        (r"NTN-F", "NTN-F"),
        (r"LFT", "LFT"),
        (r"LTN", "LTN"),
        (r"TESOURO PREFIXADO", "Tesouro Prefixado"),
        (r"FII|11\b", "FII"),
        (r"FIM|FIC|FUND", "Fundo Multimercado"),
        (r"[A-Z]{4}[0-9]{1,2}", "Ação"),
        (r"FGTS", "FGTS"),
        (r"PGBL|VGBL|PREV", "Previdência"),
    ]

    for pattern, tipo in mappings:
        if re.search(pattern, name, re.IGNORECASE):
            categoria = ASSET_TYPE_MAP.get(tipo, None)
            return tipo, categoria

    return None, None


def detect_indexer_and_rate(text: str, current_indexer: Optional[str], current_rate: Optional[object]) -> Tuple[Optional[str], Optional[float]]:
    text = normalize_text(text)
    if current_indexer:
        idx = current_indexer
    else:
        idx = None
        for pattern, label in INDEXER_PATTERNS:
            if pattern.search(text):
                idx = label
                break

    if current_rate is not None:
        try:
            return idx, float(current_rate)
        except (TypeError, ValueError):
            pass

    rate_value = None
    for pattern in RATE_PATTERNS:
        match = pattern.search(text)
        if match and match.group(1):
            rate_value = normalize_decimal(match.group(1))
            if rate_value is not None:
                break

    return idx, rate_value


def parse_number(text: str) -> Optional[float]:
    return normalize_decimal(text)
