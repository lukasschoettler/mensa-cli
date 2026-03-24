"""
Core domain models shared across scrapers and presentation layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Set

# from common.providers import SITES


@dataclass(slots=True)
class Pricing:
    """Structured pricing information for a meal."""

    raw: str
    student: Optional[float] = None
    employee: Optional[float] = None
    guest: Optional[float] = None
    is_available: bool = True


@dataclass(slots=True)
class NutritionInfo:
    """Parsed nutrition indicators such as traffic lights."""

    traffic_light: Optional[str] = None
    traffic_light_description: Optional[str] = None


@dataclass(slots=True)
class DietaryInfo:
    """Dietary labels and flags for vegetarian/vegan options."""

    labels: List[str]
    vegetarian: bool = False
    vegan: bool = False


@dataclass(slots=True)
class AllergenInfo:
    """Additive and allergen information extracted from codes."""

    codes: List[str]
    readable: List[str]
    additives: List[str]
    allergens: List[str]


@dataclass(slots=True)
class Meal:
    """Complete representation of a menu item."""

    category: str
    name: str
    pricing: Pricing
    nutrition: NutritionInfo
    dietary: DietaryInfo
    allergens: AllergenInfo


# VALID_KEYS: Set[str] = {site.key for site in SITES.values()}


@dataclass
class BaseRead:
    id: int
    timestamp: datetime

    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)


@dataclass
class MensaCreate:
    key: str
    name: str
    provider: str
    url: str
    city: str

    # def __post_init__(self):
    #     assert self.key in VALID_KEYS


@dataclass
class FetchCreate:
    html: str
    url: str
    mensa_key: str


@dataclass
class FetchRead(BaseRead):
    html: str
    url: str
    mensa_key: str


@dataclass
class MenuCreate:
    fetch_id: int
    mensa_key: str


@dataclass
class MenuRead(BaseRead):
    fetch_id: int
    mensa_key: str


@dataclass
class MealCreate:
    name: str
    mensa_key: str


@dataclass
class MealRead(BaseRead):
    name: str
    mensa_key: str
