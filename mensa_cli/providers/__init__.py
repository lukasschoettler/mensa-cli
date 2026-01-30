"""Mensa provider registry."""

from __future__ import annotations

from typing import Dict

from mensa_cli.providers.stw_berlin import parser as stw_parser
from mensa_cli.providers.types import MensaSite

SITES: Dict[str, MensaSite] = {
    "hu_sued": MensaSite(
        key="hu_sued",
        name="Mensa HU Süd",
        url="https://www.stw.berlin/mensen/einrichtungen/humboldt-universität-zu-berlin/mensa-hu-süd.html",
        provider="stw_berlin",
        city="Berlin",
        parser=stw_parser.parse_menu,
    ),
    "hu_nord": MensaSite(
        key="hu_nord",
        name="Mensa HU Nord",
        url="https://www.stw.berlin/mensen/einrichtungen/humboldt-universität-zu-berlin/mensa-hu-nord.html",
        provider="stw_berlin",
        city="Berlin",
        parser=stw_parser.parse_menu,
    ),
    "bht": MensaSite(
        key="bht",
        name="BHT",
        url="https://www.stw.berlin/mensen/einrichtungen/berliner-hochschule-für-technik/mensa-bht.html",
        provider="stw_berlin",
        city="Berlin",
        parser=stw_parser.parse_menu,
    ),
}
