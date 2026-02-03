"""Module entry point for ``python -m mensa_cli``."""

from __future__ import annotations

from mensa_cli.cli import app


def main() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
