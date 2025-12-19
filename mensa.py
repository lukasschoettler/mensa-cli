#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
import typer
from urllib.parse import urlsplit, urlunsplit, quote

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

def normalize_url(url: str) -> str:
    """
    Ensures the URL is properly percent-encoded.
    """
    parts = urlsplit(url)
    path = quote(parts.path)
    query = quote(parts.query, safe="=&")
    return urlunsplit((
        parts.scheme,
        parts.netloc,
        path,
        query,
        parts.fragment,
    ))

app = typer.Typer()
console = Console()

MENU_URL = "https://www.stw.berlin/mensen/einrichtungen/humboldt-universität-zu-berlin/mensa-hu-süd.html"

def fetch_page(url: str) -> str:
    normalized = normalize_url(url)
    resp = requests.get(normalized,
                        timeout=10,
                        headers=HEADERS )
    resp.raise_for_status()
    return resp.text

def parse_menu(html: str):
    soup = BeautifulSoup(html, "html.parser")

    speiseplan = soup.find("div", id="speiseplan")
    if not speiseplan:
        raise RuntimeError("div#speiseplan not found")

    results = []

    # Iterate over category blocks
    for group in speiseplan.find_all("div", class_="splGroupWrapper", recursive=False):
        group_name_el = group.find("div", class_="splGroup")
        if not group_name_el:
            continue

        category = group_name_el.get_text(strip=True)

        # Iterate over meals in this category
        for meal in group.find_all("div", class_="splMeal", recursive=False):
            # Name
            name_el = meal.find("span", class_="bold")
            name = name_el.get_text(strip=True) if name_el else ""

            # Allergens / additives
            allergens = meal.get("data-kennz", "").strip()

            # Price (right-aligned column)
            price = ""
            price_col = meal.find("div", class_="text-right")
            if price_col:
                price = price_col.get_text(strip=True).replace("€", "").strip()

            # Optional labels from icons (vegan, vegetarisch, ampel)
            labels = []
            for img in meal.find_all("img", class_="splIcon"):
                alt = img.get("alt", "")
                if alt:
                    labels.append(BeautifulSoup(alt, "html.parser").get_text())

            results.append({
                "category": category,
                "name": name,
                "allergens": allergens,
                "price": price,
                "labels": ", ".join(labels),
            })

    return results

def print_table(menu_data):
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Section")
    table.add_column("Dish")
    table.add_column("Allergens")
    table.add_column("Price")

    for item in menu_data:
        table.add_row(item["category"], item["name"], item["allergens"], item["price"])

    console.print(table)

@app.command()
def scrape(url: str = MENU_URL):
    """
    Scrape a Mensa menu from the given URL and print it.
    """
    console.print(f"[blue]Fetching menu from:[/] {url}")
    html = fetch_page(url)

    console.print("[blue]Parsing menu...[/]")
    menu_data = parse_menu(html)

    if not menu_data:
        console.print("[yellow]No dishes found — maybe the structure differs?[/]")
        return

    print_table(menu_data)

if __name__ == "__main__":
    app()
