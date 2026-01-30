"""Presentation helpers using Rich for terminal output."""

from __future__ import annotations

from typing import Sequence

from rich.console import Console
from rich.table import Table

from mensa_cli.models import Meal
from mensa_cli.providers.types import MensaSite


def create_meal_table(
    meals: Sequence[Meal],
    *,
    show_allergens: bool = True,
    show_prices: bool = True,
    price_tier: str = "student",
    show_nutrition: bool = True,
    show_dietary: bool = True,
) -> Table:
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Category", style="cyan")
    table.add_column("Dish", style="white")

    if show_dietary:
        table.add_column("Dietary", style="magenta")

    if show_nutrition:
        table.add_column("Nutrition", style="yellow")

    if show_allergens:
        table.add_column("Allergens", style="red")

    if show_prices:
        table.add_column("Price", style="green", justify="right")

    for meal in meals:
        columns = [meal.category, meal.name]

        if show_dietary:
            dietary_text = ", ".join(meal.dietary.labels) if meal.dietary.labels else ""
            columns.append(dietary_text)

        if show_nutrition:
            columns.append(meal.nutrition.traffic_light or "")

        if show_allergens:
            allergen_text = (
                ", ".join(meal.allergens.codes) if meal.allergens.codes else ""
            )
            columns.append(allergen_text)

        if show_prices:
            columns.append(_format_price(meal, price_tier))

        table.add_row(*columns)

    return table


def print_list(console: Console, mensen: dict[str, MensaSite]) -> Table:
    console.print("\n[bold blue]Available Mensas:[/]")

    table = Table(show_header=True, header_style="bold green")
    table.add_column("City")
    table.add_column("ID")
    table.add_column("Mensa")
    table.add_column("URL")

    for key in mensen:
        columns = [mensen[key].city, mensen[key].key, mensen[key].name, mensen[key].url]
        table.add_row(*columns)

    return table


def print_summary(console: Console, meals: Sequence[Meal]) -> None:
    console.print("\n[bold blue]Summary Statistics:[/]")

    categories = {meal.category for meal in meals}
    vegetarian_count = sum(1 for meal in meals if meal.dietary.vegetarian)
    vegan_count = sum(1 for meal in meals if meal.dietary.vegan)

    console.print(f"• Total meals: {len(meals)}")
    console.print(f"• Categories: {', '.join(sorted(categories))}")
    console.print(f"• Vegetarian options: {vegetarian_count}")
    console.print(f"• Vegan options: {vegan_count}")

    traffic_lights: dict[str, int] = {}
    for meal in meals:
        light = meal.nutrition.traffic_light or "Unknown"
        traffic_lights[light] = traffic_lights.get(light, 0) + 1

    if traffic_lights:
        console.print("• Nutrition distribution:")
        for light, count in traffic_lights.items():
            console.print(f"  - {light}: {count}")


def _format_price(meal: Meal, tier: str) -> str:
    pricing = meal.pricing
    if not pricing.is_available:
        return ""

    if tier == "student" and pricing.student is not None:
        return f"€{pricing.student:.2f}"
    if tier == "employee" and pricing.employee is not None:
        return f"€{pricing.employee:.2f}"
    if tier == "guest" and pricing.guest is not None:
        return f"€{pricing.guest:.2f}"
    return pricing.raw
