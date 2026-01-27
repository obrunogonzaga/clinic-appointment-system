from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class ClientRegistry:
    by_bank: Dict[str, Dict[str, str]]

    @classmethod
    def from_csv(cls, path: Path) -> "ClientRegistry":
        data: Dict[str, Dict[str, str]] = {}
        if path.exists():
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    bank = (row.get("Banco") or "").upper()
                    if not bank:
                        continue
                    data[bank] = {
                        "Nome": row.get("Nome", ""),
                        "CodigoXP": row.get("CodigoXP", "0"),
                        "CodigoBTG": row.get("CodigoBTG", "0"),
                    }
        return cls(by_bank=data)

    def defaults_for_bank(self, bank: str) -> Dict[str, str]:
        return self.by_bank.get(bank.upper(), {"Nome": "", "CodigoXP": "0", "CodigoBTG": "0"})
