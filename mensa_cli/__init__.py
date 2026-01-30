from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from typer import Typer

    app: Typer

__all__ = ["app"]


def __getattr__(name: str) -> Any:
    if name == "app":
        from .cli import app as cli_app

        return cli_app
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
