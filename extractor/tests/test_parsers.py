from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from parsers import BTGParser, BradescoParser, ItauParser, XPParser
from utils.clients import ClientRegistry

SAMPLES_DIR = Path(__file__).parent / "samples"
CLIENT_REGISTRY = ClientRegistry.from_csv(Path(__file__).resolve().parents[1] / "data" / "base_clientes.csv")


def _parse(parser_cls):
    sample_name = parser_cls.__name__.replace("Parser", "").lower() + "_sample.pdf"
    path = SAMPLES_DIR / sample_name
    parser = parser_cls(client_defaults=CLIENT_REGISTRY.defaults_for_bank(parser_cls.bank_name))
    result = parser.parse(path)
    return result


def test_itau_parser_extracts_rows():
    result = _parse(ItauParser)
    assert result["bank"] == "ITÁU"
    assert result["position_date"] == "2025-09-15"
    assert result["items"]
    first = result["items"][0]
    assert first["Ativo"]
    assert first["Tipo de ativo"] == "CDB"
    assert first["Categoria"] == "Renda Fixa"
    assert first["Indexador"] == "CDI"
    assert first["Taxa (%)"] == 100.0
    assert first["Vencimento"] == "2030-08-14"


def test_xp_parser_extracts_rows():
    result = _parse(XPParser)
    assert result["bank"] == "XP"
    assert result["position_date"] == "2025-09-30"
    first = result["items"][0]
    assert first["Tipo de ativo"] == "LCA"
    assert first["Categoria"] == "Renda Fixa"
    assert first["Indexador"] == "PRE"
    assert first["Taxa (%)"] == 11.6
    assert first["Vencimento"] == "2027-05-01"


def test_bradesco_parser_extracts_rows():
    result = _parse(BradescoParser)
    assert result["bank"] == "BRADESCO"
    assert result["position_date"] == "2025-10-01"
    first = result["items"][0]
    assert first["Tipo de ativo"] == "LIG"
    assert first["Categoria"] == "Renda Fixa"
    assert first["Indexador"] == "PRE"
    assert first["Taxa (%)"] == 12.79


def test_btg_parser_extracts_rows():
    result = _parse(BTGParser)
    assert result["bank"] == "BTG"
    assert result["position_date"] == "2025-09-01"
    first = result["items"][0]
    assert first["Tipo de ativo"] == "DEB"
    assert first["Categoria"] == "Renda Fixa"
    assert first["Indexador"] == "IPC-A"
    assert first["Taxa (%)"] == 7.44
