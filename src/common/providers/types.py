"""Registry types for Mensa providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Dict,
    ItemsView,
    Iterator,
    KeysView,
    List,
    Optional,
    Protocol,
    ValuesView,
    runtime_checkable,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from common.models import Meal


@dataclass(slots=True)
class ParseResult:
    """Structured response returned by a parser implementation."""

    meals: List[Meal]
    menu_date: Optional[str] = None
    source_url: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        from common.models import Meal

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
    city: str
    parser: Parser


@dataclass(frozen=True, slots=True)
class MensaRegistry:
    """Immutable registry of Mensa sites."""

    _sites: Dict[str, MensaSite]

    def __iter__(self) -> Iterator[tuple[str, MensaSite]]:
        return iter(self._sites.items())

    def __getitem__(self, key: str) -> MensaSite:
        return self._sites[key]

    def __len__(self) -> int:
        return len(self._sites)

    def __contains__(self, key: str) -> bool:
        return key in self._sites

    def get(self, key: str, default: Optional[MensaSite] = None) -> Optional[MensaSite]:
        return self._sites.get(key, default)

    def keys(self) -> KeysView[str]:
        return self._sites.keys()

    def values(self) -> ValuesView[MensaSite]:
        return self._sites.values()

    def items(self) -> ItemsView[str, MensaSite]:
        return self._sites.items()
