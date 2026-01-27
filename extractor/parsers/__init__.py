from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Type

from utils.fuzzy import CNPJMatcher

from .base import BaseParser, ParseError
from .itau import ItauParser
from .xp import XPParser
from .bradesco import BradescoParser
from .btg import BTGParser

PARSERS: List[Type[BaseParser]] = [
    ItauParser,
    XPParser,
    BradescoParser,
    BTGParser,
]


def detect_parser(text: str, hint: Optional[str] = None) -> Optional[Type[BaseParser]]:
    if hint:
        hint = hint.lower()
        for parser in PARSERS:
            if parser.bank_name.lower() == hint:
                return parser
    for parser in PARSERS:
        if parser.matches(text):
            return parser
    return None


def build_parser(
    parser_cls: Type[BaseParser],
    cnpj_matcher: Optional[CNPJMatcher] = None,
    client_defaults: Optional[dict] = None,
) -> BaseParser:
    return parser_cls(cnpj_matcher=cnpj_matcher, client_defaults=client_defaults)


__all__ = [
    "BaseParser",
    "ParseError",
    "detect_parser",
    "build_parser",
]
