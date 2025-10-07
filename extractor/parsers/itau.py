from __future__ import annotations

import re
from typing import Dict, List, Optional, Sequence

from utils.normalization import normalize_money, normalize_decimal, parse_date, detect_indexer_and_rate, classify_asset

from .base import BaseParser, iter_text_lines


class ItauParser(BaseParser):
    bank_name = "ITÁU"

    @classmethod
    def matches(cls, text: str) -> bool:
        text_upper = text.upper()
        return "PRIVATE BANK" in text_upper and "DETALHAMENTO DE ATIVOS" in text_upper

    def extract_position_date(self, pages_text: Sequence[str]) -> Optional[str]:
        for line in iter_text_lines(pages_text):
            match = re.search(r"Data da posição\s*[:|-]\s*(.+)", line, re.IGNORECASE)
            if match:
                parsed = parse_date(match.group(1))
                if parsed:
                    return parsed
        return None

    def extract_items(self, pages_text: Sequence[str], position_date: str) -> List[Dict[str, object]]:
        collecting = False
        items: List[Dict[str, object]] = []
        for line in iter_text_lines(pages_text):
            upper_line = line.upper()
            if "DETALHAMENTO DE ATIVOS" in upper_line:
                collecting = True
                continue
            if collecting:
                parts = [chunk.strip() for chunk in line.split(";")]
                if len(parts) < 6:
                    continue
                ativo, venc, valor, quantidade, preco, saldo = parts[:6]
                idx, taxa = detect_indexer_and_rate(ativo, None, None)
                tipo, categoria = classify_asset(ativo)
                items.append(
                    {
                        "Ativo": ativo,
                        "Vencimento": parse_date(venc) or venc,
                        "Valor": normalize_money(valor) or normalize_money(saldo),
                        "Quantidade": normalize_decimal(quantidade),
                        "Preco": normalize_decimal(preco),
                        "Indexador": idx,
                        "Taxa": taxa,
                        "Tipo": tipo,
                        "Categoria": categoria,
                    }
                )
        return items
