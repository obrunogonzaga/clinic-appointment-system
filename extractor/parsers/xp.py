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


class XPParser(BaseParser):
    bank_name = "XP"

    @classmethod
    def matches(cls, text: str) -> bool:
        upper = text.upper()
        return "XP INVESTIMENTOS" in upper and "POSIÇÃO DETALHADA DOS ATIVOS" in upper

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
            if "POSIÇÃO DETALHADA DOS ATIVOS" in upper:
                capturing = True
                continue
            if not capturing:
                continue
            parts = [chunk.strip() for chunk in line.split(";")]
            if len(parts) < 4:
                # fallback to regex splitting by two spaces
                parts = re.split(r"\s{2,}", line.strip())
            if len(parts) < 4:
                continue
            ativo = parts[0]
            valor = parts[1]
            preco = parts[2]
            vencimento = parse_date(parts[3]) or parts[3]
            idx, taxa = detect_indexer_and_rate(ativo, None, None)
            tipo, categoria = classify_asset(ativo)
            items.append(
                {
                    "Ativo": ativo,
                    "Valor": normalize_money(valor),
                    "Preco": normalize_decimal(preco),
                    "Vencimento": vencimento,
                    "Indexador": idx,
                    "Taxa": taxa,
                    "Tipo": tipo,
                    "Categoria": categoria,
                }
            )
        return items
