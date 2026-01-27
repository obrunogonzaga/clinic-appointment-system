from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import pdfplumber
import structlog

from utils.normalization import (
    classify_asset,
    detect_indexer_and_rate,
    ensure_iso_date,
    normalize_decimal,
    normalize_money,
    normalize_text,
)
from utils.fuzzy import CNPJMatcher

try:
    import pytesseract  # type: ignore
    from pdf2image import convert_from_path  # type: ignore
except Exception:  # pragma: no cover - optional dependency at runtime
    pytesseract = None
    convert_from_path = None


class ParseError(RuntimeError):
    """Raised when a parser cannot extract the expected content."""


class BaseParser(ABC):
    bank_name: str = ""

    def __init__(
        self,
        cnpj_matcher: Optional[CNPJMatcher] = None,
        client_defaults: Optional[dict] = None,
    ) -> None:
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.cnpj_matcher = cnpj_matcher
        self.client_defaults = client_defaults or {}

    @classmethod
    @abstractmethod
    def matches(cls, text: str) -> bool:
        """Return True when the parser recognises the statement layout."""

    @abstractmethod
    def extract_position_date(self, pages_text: Sequence[str]) -> Optional[str]:
        """Return the ISO formatted position date if found."""

    @abstractmethod
    def extract_items(self, pages_text: Sequence[str], position_date: str) -> List[Dict[str, object]]:
        """Return raw investment rows for the statement."""

    def parse(self, pdf_path: Path) -> Dict[str, object]:
        pages_text = self._extract_text(pdf_path)
        if not any(pages_text):
            raise ParseError("PDF does not contain extractable text")

        position_date = self.extract_position_date(pages_text)
        if not position_date:
            raise ParseError("Unable to find position date")

        items = self.extract_items(pages_text, position_date)
        if not items:
            raise ParseError("No investment rows were detected")

        enriched = [self._post_process(item, position_date) for item in items]
        return {
            "bank": self.bank_name,
            "position_date": position_date,
            "items": enriched,
        }

    def _post_process(self, item: Dict[str, object], position_date: str) -> Dict[str, object]:
        default_xp = self.client_defaults.get("CodigoXP", 0)
        default_btg = self.client_defaults.get("CodigoBTG", 0)
        try:
            default_xp = int(default_xp)
        except (TypeError, ValueError):
            default_xp = 0
        try:
            default_btg = int(default_btg)
        except (TypeError, ValueError):
            default_btg = 0

        base = {
            "Banco": self.bank_name,
            "DATA": position_date,
            "Código XP": item.get("CodigoXP") or default_xp,
            "Código BTG": item.get("CodigoBTG") or default_btg,
            "Nome": item.get("Nome") or self.client_defaults.get("Nome", ""),
            "Ativo": normalize_text(str(item.get("Ativo", ""))),
            "Preço": item.get("Preco"),
            "Valor": item.get("Valor"),
            "Tipo de ativo": item.get("Tipo"),
            "Categoria": item.get("Categoria"),
            "Indexador": item.get("Indexador"),
            "Taxa (%)": item.get("Taxa"),
            "Vencimento": ensure_iso_date(item.get("Vencimento")),
            "CNPJ": item.get("CNPJ", ""),
        }

        if not base["Tipo de ativo"] or not base["Categoria"]:
            tipo, categoria = classify_asset(base["Ativo"])
            base["Tipo de ativo"] = base["Tipo de ativo"] or tipo
            base["Categoria"] = base["Categoria"] or categoria

        if not base["Indexador"] or base["Taxa (%)"] is None:
            idx, taxa = detect_indexer_and_rate(
                base["Ativo"],
                base["Indexador"],
                base["Taxa (%)"],
            )
            base["Indexador"] = base["Indexador"] or idx
            base["Taxa (%)"] = base["Taxa (%)"] if base["Taxa (%)"] is not None else taxa

        if isinstance(base["Valor"], str):
            base["Valor"] = normalize_money(base["Valor"])
        if isinstance(base["Preço"], str):
            base["Preço"] = normalize_decimal(base["Preço"])
        if isinstance(base["Taxa (%)"], str):
            base["Taxa (%)"] = normalize_decimal(base["Taxa (%)"])

        if self.cnpj_matcher and not base["CNPJ"]:
            cnpj = self.cnpj_matcher.match(base["Ativo"])
            if cnpj:
                base["CNPJ"] = cnpj

        return base

    def _extract_text(self, pdf_path: Path) -> List[str]:
        pages_text: List[str] = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                pages_text.append(text)

        if not any(pages_text) and pytesseract and convert_from_path:
            pages_text = self._extract_text_with_ocr(pdf_path)

        return pages_text

    def _extract_text_with_ocr(self, pdf_path: Path) -> List[str]:
        if not pytesseract or not convert_from_path:
            return []
        images = convert_from_path(str(pdf_path))
        texts: List[str] = []
        for image in images:
            text = pytesseract.image_to_string(image, lang="por")
            texts.append(text)
        return texts


def iter_text_lines(pages_text: Sequence[str]) -> Iterable[str]:
    for page in pages_text:
        for line in page.splitlines():
            if line.strip():
                yield line.strip()
