"""Registry types for Mensa providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, List, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:  # pragma: no cover - typing only
    from mensa.models import Meal


@dataclass(slots=True)
class ParseResult:
    """Structured response returned by a parser implementation."""

    meals: List["Meal"]
    menu_date: Optional[str] = None
    source_url: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        from mensa.models import Meal

        if not isinstance(self.meals, list):
            object.__setattr__(self, "meals", list(self.meals))

        for meal in self.meals:
            if not isinstance(meal, Meal):
                raise TypeError("ParseResult.meals must contain Meal instances")


@runtime_checkable
class Parser(Protocol):
    """Callable contract for provider parsers."""

    def __call__(self, html: str) -> ParseResult:
        """Parse raw HTML and return structured meal data."""
        ...


@dataclass(frozen=True)
class MensaSite:
    """Descriptor for a single Mensa location."""

    key: str
    name: str
    url: str
    provider: str
    city: Optional[str]
    parser: Parser
