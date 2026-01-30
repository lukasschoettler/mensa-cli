"""Mensa provider registry."""

from __future__ import annotations

from typing import Dict

# from mensa_cli.models import Meal
from mensa_cli.providers.types import MensaSite
from mensa_cli.providers.stw_berlin import parser as stw_parser

SITES: Dict[str, MensaSite] = {
    "hu_sued": MensaSite(
        key="hu_sued",
        name="Mensa HU Süd",
        url="https://www.stw.berlin/mensen/einrichtungen/humboldt-universität-zu-berlin/mensa-hu-süd.html",
        provider="stw_berlin",
        city="Berlin",
        parser=stw_parser.parse_menu,
    ),
}
