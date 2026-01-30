"""Registry types for Mensa providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:  # pragma: no cover - typing only
    from mensa_cli.models import Meal

Parser = Callable[[str], List["Meal"]]


@dataclass(frozen=True)
class MensaSite:
    """Descriptor for a single Mensa location."""

    key: str
    name: str
    url: str
    provider: str
    city: Optional[str]
    parser: Parser
