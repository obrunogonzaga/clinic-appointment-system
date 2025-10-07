from __future__ import annotations

import base64
import io
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import structlog
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from parsers import ParseError, build_parser, detect_parser
from utils.clients import ClientRegistry
from utils.fuzzy import CNPJMatcher

app = FastAPI(title="PDF Investment Extractor")
logger = structlog.get_logger("pdf-extractor")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

cnpj_matcher = CNPJMatcher.from_csv(DATA_DIR / "cnpj_map.csv")
client_registry = ClientRegistry.from_csv(DATA_DIR / "base_clientes.csv")


class EnrichmentOptions(BaseModel):
    try_cnpj_match: bool = Field(default=False, description="Attempt to enrich assets with CNPJ")


class ExtractRequest(BaseModel):
    filename: str
    file_b64: str
    bank_hint: str = Field(default="auto", description="Optional bank hint: auto|itau|xp|bradesco|btg")
    return_format: str = Field(default="json", description="json or csv")
    enrichment: EnrichmentOptions = Field(default_factory=EnrichmentOptions)


class ExtractResponse(BaseModel):
    bank: str
    position_date: str
    items: list[dict]
    csv: Optional[str] = None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest) -> ExtractResponse:
    try:
        pdf_bytes = base64.b64decode(request.file_b64)
    except Exception as exc:  # pragma: no cover - validation handled by pydantic
        raise HTTPException(status_code=400, detail=f"Invalid base64 payload: {exc}")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp.flush()
        temp_path = Path(tmp.name)

    try:
        text_snapshot = _read_pdf_text(temp_path)
        parser_cls = detect_parser(text_snapshot, hint=_normalize_hint(request.bank_hint))
        if not parser_cls:
            raise HTTPException(status_code=422, detail="Unable to detect the statement layout")

        defaults = client_registry.defaults_for_bank(parser_cls.bank_name)
        parser = build_parser(
            parser_cls,
            cnpj_matcher=cnpj_matcher if request.enrichment.try_cnpj_match else None,
            client_defaults=defaults,
        )
        result = parser.parse(temp_path)
    except ParseError as exc:
        logger.error("parse_error", error=str(exc))
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        temp_path.unlink(missing_ok=True)

    items = result.get("items", [])
    csv_payload: Optional[str] = None
    if request.return_format.lower() == "csv":
        df = pd.DataFrame(items)
        output = io.StringIO()
        df.to_csv(output, index=False)
        csv_payload = output.getvalue()

    response = ExtractResponse(
        bank=result.get("bank", ""),
        position_date=result.get("position_date", ""),
        items=items,
        csv=csv_payload,
    )
    return response


def _read_pdf_text(path: Path) -> str:
    import pdfplumber

    pages: list[str] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
            pages.append(text)
    return "\n".join(pages)


def _normalize_hint(hint: str) -> Optional[str]:
    hint = (hint or "").strip().lower()
    if hint in {"auto", ""}:
        return None
    mapping = {
        "itau": "itáu",
        "itaú": "itáu",
        "xp": "xp",
        "bradesco": "bradesco",
        "btg": "btg",
    }
    return mapping.get(hint, hint)


__all__ = ["app"]
