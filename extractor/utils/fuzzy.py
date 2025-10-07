from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from rapidfuzz import fuzz


@dataclass
class CNPJMatcher:
    rows: List[tuple[str, str]]
    threshold: int = 90

    @classmethod
    def from_csv(cls, csv_path: Path) -> "CNPJMatcher":
        rows: List[tuple[str, str]] = []
        if csv_path.exists():
            with csv_path.open("r", newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    name = row.get("name") or row.get("Nome") or ""
                    cnpj = row.get("cnpj") or row.get("CNPJ") or ""
                    if name and cnpj:
                        rows.append((name.upper(), cnpj))
        return cls(rows=rows)

    def match(self, asset_name: str) -> Optional[str]:
        if not asset_name:
            return None
        candidate = asset_name.upper()
        best_score = 0
        best_cnpj: Optional[str] = None
        for name, cnpj in self.rows:
            score = fuzz.token_sort_ratio(candidate, name)
            if score > best_score and score >= self.threshold:
                best_score = score
                best_cnpj = cnpj
        return best_cnpj
