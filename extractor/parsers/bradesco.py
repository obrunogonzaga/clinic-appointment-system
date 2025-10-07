from __future__ import annotations

import re
from typing import Dict, List, Optional, Sequence

from utils.normalization import (
    classify_asset,
    detect_indexer_and_rate,
    normalize_decimal,
    normalize_money,
    parse_date,
)

from .base import BaseParser, iter_text_lines


class BradescoParser(BaseParser):
    bank_name = "BRADESCO"

    @classmethod
    def matches(cls, text: str) -> bool:
        upper = text.upper()
        return "BRADESCO" in upper and "POSIÇÃO DETALHADA DOS INVESTIMENTOS" in upper

    def extract_position_date(self, pages_text: Sequence[str]) -> Optional[str]:
        for line in iter_text_lines(pages_text):
            match = re.search(r"Data de refer[êe]ncia\s*[:|-]\s*(.+)", line, re.IGNORECASE)
            if match:
                parsed = parse_date(match.group(1))
                if parsed:
                    return parsed
        return None

    def extract_items(self, pages_text: Sequence[str], position_date: str) -> List[Dict[str, object]]:
        capturing = False
        items: List[Dict[str, object]] = []
        for line in iter_text_lines(pages_text):
            upper = line.upper()
            if "POSIÇÃO DETALHADA DOS INVESTIMENTOS" in upper:
                capturing = True
                continue
            if not capturing:
                continue
            parts = [chunk.strip() for chunk in line.split(";")]
            if len(parts) < 5:
                continue
            ativo, valor_aplicado, taxa, preco_atual, valor_bruto = parts[:5]
            idx, taxa_value = detect_indexer_and_rate(f"{ativo} {taxa}", None, None)
            tipo, categoria = classify_asset(ativo)
            items.append(
                {
                    "Ativo": ativo,
                    "Valor": normalize_money(valor_bruto) or normalize_money(valor_aplicado),
                    "Preco": normalize_decimal(preco_atual),
                    "Indexador": idx,
                    "Taxa": taxa_value or normalize_decimal(taxa),
                    "Tipo": tipo,
                    "Categoria": categoria,
                }
            )
        return items
