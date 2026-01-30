"""Parser implementation for STW Berlin-based Mensa sites."""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup, Tag

from mensa_cli.models import AllergenInfo, DietaryInfo, Meal, NutritionInfo, Pricing
from mensa_cli.providers.stw_berlin import constants

logger = logging.getLogger(__name__)


def _get_text(element: Optional[Tag], default: str = "") -> str:
    if element is None:
        return default
    return element.get_text(strip=True)


def _get_attribute(element: Optional[Tag], attribute: str, default: str = "") -> str:
    if element is None:
        return default
    value = element.get(attribute)
    if value is None:
        return default
    return str(value)


def _parse_price_string(price_text: str) -> Pricing:
    if not price_text or not price_text.strip():
        return Pricing(raw="", is_available=False)

    cleaned = re.sub(r"[€\s]", "", price_text.strip())
    if not cleaned:
        return Pricing(raw=price_text, is_available=False)

    student = employee = guest = None

    try:
        price_parts = [part.strip() for part in cleaned.split("/") if part.strip()]

        if len(price_parts) >= 1:
            student = float(price_parts[0].replace(",", "."))
        if len(price_parts) >= 2:
            employee = float(price_parts[1].replace(",", "."))
        if len(price_parts) >= 3:
            guest = float(price_parts[2].replace(",", "."))
    except (ValueError, IndexError) as exc:
        logger.warning("Failed to parse price '%s': %s", price_text, exc)
        return Pricing(raw=price_text, is_available=True)

    return Pricing(
        raw=price_text,
        student=student,
        employee=employee,
        guest=guest,
        is_available=True,
    )


def _parse_allergen_codes(allergen_string: str) -> AllergenInfo:
    if not allergen_string:
        return AllergenInfo(codes=[], readable=[], additives=[], allergens=[])

    codes = [code.strip() for code in allergen_string.split(",") if code.strip()]

    readable: List[str] = []
    additives: List[str] = []
    allergens: List[str] = []

    for code in codes:
        info = constants.ALLERGEN_ADDITIVES.get(code)
        if info is None:
            readable.append(code)
            allergens.append(code)
            continue

        readable.append(info["description"])
        if info["type"] == "additive":
            additives.append(info["name"])
        elif info["type"] == "allergen":
            allergens.append(info["name"])

    return AllergenInfo(
        codes=codes, readable=readable, additives=additives, allergens=allergens
    )


def _parse_icons(meal_element: Tag) -> Tuple[NutritionInfo, DietaryInfo]:
    nutrition = NutritionInfo()
    dietary_labels: List[str] = []
    is_vegetarian = False
    is_vegan = False

    icons = meal_element.find_all("img", class_="splIcon")

    for icon in icons:
        src = _get_attribute(icon, "src")
        if not src:
            continue

        traffic_key = next(
            (key for key in constants.TRAFFIC_LIGHT_MAP if key in src),
            None,
        )
        if traffic_key:
            traffic_info = constants.TRAFFIC_LIGHT_MAP[traffic_key]
            nutrition.traffic_light = traffic_info["name"]
            nutrition.traffic_light_description = traffic_info["description"]
            continue

        icon_name = src.split("/")[-1]
        dietary_info = constants.DIETARY_ICON_MAP.get(icon_name)
        if dietary_info:
            dietary_labels.append(dietary_info["name"])
            if dietary_info["name"] == "Vegetarisch":
                is_vegetarian = True
            elif dietary_info["name"] == "Vegan":
                is_vegan = True
                is_vegetarian = True

    dietary = DietaryInfo(
        labels=dietary_labels, vegetarian=is_vegetarian, vegan=is_vegan
    )
    return nutrition, dietary


def _parse_meal(meal_element: Tag) -> Optional[Meal]:
    name_element = meal_element.find("span", class_="bold")
    if name_element is None:
        logger.warning("No name element found in meal")
        return None

    name = _get_text(name_element)
    if not name:
        logger.warning("Empty meal name found")
        return None

    allergen_codes_raw = _get_attribute(meal_element, "data-kennz", "")
    allergens = _parse_allergen_codes(allergen_codes_raw)

    price_element = meal_element.find("div", class_="text-right")
    price_text = _get_text(price_element)
    pricing = _parse_price_string(price_text)

    nutrition, dietary = _parse_icons(meal_element)

    return Meal(
        category="",
        name=name,
        pricing=pricing,
        nutrition=nutrition,
        dietary=dietary,
        allergens=allergens,
    )


def parse_menu(html: str) -> List[Meal]:
    soup = BeautifulSoup(html, "html.parser")

    speiseplan = soup.find("div", id="speiseplan")
    if speiseplan is None:
        raise RuntimeError("div#speiseplan not found")

    meals: List[Meal] = []

    groups = speiseplan.find_all("div", class_="splGroupWrapper", recursive=False)
    for group in groups:
        group_name_element = group.find("div", class_="splGroup")
        if group_name_element is None:
            logger.warning("No category name found in group wrapper")
            continue

        category = _get_text(group_name_element)
        meal_elements = group.find_all("div", class_="splMeal", recursive=False)

        for meal_element in meal_elements:
            meal = _parse_meal(meal_element)
            if meal:
                meal.category = category
                meals.append(meal)

    return meals
