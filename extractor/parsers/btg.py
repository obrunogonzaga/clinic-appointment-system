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


class BTGParser(BaseParser):
    bank_name = "BTG"

    @classmethod
    def matches(cls, text: str) -> bool:
        upper = text.upper()
        return "BTG" in upper and "RENDA FIXA" in upper

    def extract_position_date(self, pages_text: Sequence[str]) -> Optional[str]:
        for line in iter_text_lines(pages_text):
            match = re.search(r"Data\s*[:|-]\s*(\d{2}/\d{2}/\d{4})", line)
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
            if "RENDA FIXA" in upper:
                capturing = True
                continue
            if not capturing:
                continue
            parts = [chunk.strip() for chunk in line.split(";")]
            if len(parts) < 5:
                continue
            ativo, taxa_media, quantidade, preco, saldo = parts[:5]
            idx, taxa = detect_indexer_and_rate(f"{ativo} {taxa_media}", None, None)
            tipo, categoria = classify_asset(ativo)
            items.append(
                {
                    "Ativo": ativo,
                    "Valor": normalize_money(saldo),
                    "Preco": normalize_decimal(preco),
                    "Indexador": idx,
                    "Taxa": taxa,
                    "Quantidade": normalize_decimal(quantidade),
                    "Tipo": tipo,
                    "Categoria": categoria,
                }
            )
        return items
