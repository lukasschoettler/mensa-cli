"""Typer-based CLI entry point."""

from __future__ import annotations

import logging
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

if __package__ in {None, ""}:  # pragma: no cover - execution as script
    import sys
    from pathlib import Path

    package_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(package_dir.parent))
    globals()["__package__"] = package_dir.name

from . import http, presentation
from .providers import SITES
from .providers.types import MensaSite

logger = logging.getLogger(__name__)

app = typer.Typer(help="Scrape Mensa menus from supported providers.")
console = Console()


def _validate_price_tier(value: str) -> str:
    allowed = {"student", "employee", "guest"}
    if value not in allowed:
        raise typer.BadParameter(
            f"Price tier must be one of {', '.join(sorted(allowed))}"
        )
    return value


@app.callback()
def configure(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    )
) -> None:
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")


@app.command()
def list() -> None:
    """List available Mensas"""
    table = presentation.print_list(console=console, mensen=SITES)

    console.print(table)


@app.command()
def scrape(
    mensa: str = typer.Option(
        "hu_sued",
        "--mensa",
        "-m",
        help="Key of the mensa to scrape",
        show_default=True,
    ),
    price_tier: str = typer.Option(
        "student",
        "--price-tier",
        help="Price tier to show (student/employee/guest)",
        show_default=True,
    ),
    show_allergens: bool = typer.Option(
        True, "--allergens/--no-allergens", help="Show allergen information"
    ),
    show_prices: bool = typer.Option(
        True, "--prices/--no-prices", help="Show price information"
    ),
    show_nutrition: bool = typer.Option(
        True, "--nutrition/--no-nutrition", help="Show nutrition traffic lights"
    ),
    show_dietary: bool = typer.Option(
        True, "--dietary/--no-dietary", help="Show dietary labels"
    ),
    summary: bool = typer.Option(
        False, "--summary", "-s", help="Show summary statistics"
    ),
) -> None:
    price_tier = _validate_price_tier(price_tier)

    site = _resolve_site(mensa)

    console.print(f"[blue]Fetching menu from:[/] {site.url}")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching menu...", total=None)
        html = http.fetch_html(site.url)
        progress.update(task, description="Menu fetched successfully!")

    console.print("[blue]Parsing menu...[/]")
    meals = site.parser(html)
    if not meals:
        console.print("[yellow]No dishes found — maybe the structure differs?[/]")
        return

    console.print(f"[green]Successfully parsed {len(meals)} meals![/]")

    table = presentation.create_meal_table(
        meals,
        show_allergens=show_allergens,
        show_prices=show_prices,
        price_tier=price_tier,
        show_nutrition=show_nutrition,
        show_dietary=show_dietary,
    )
    console.print(table)

    if summary:
        presentation.print_summary(console, meals)


def _resolve_site(key: str) -> MensaSite:
    try:
        return SITES[key]
    except KeyError as exc:
        available = ", ".join(sorted(SITES))
        raise typer.BadParameter(
            f"Unknown mensa '{key}'. Available: {available}"
        ) from exc
