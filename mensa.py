#!/usr/bin/env python3

from urllib.parse import quote, urlsplit, urlunsplit
import re
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

import requests
import typer
from bs4 import BeautifulSoup, Tag
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Comprehensive mappings for allergen and additive codes
ALLERGEN_ADDITIVES = {
    # Additives
    "2": {"name": "Schweinefleisch", "type": "additive", "description": "Schweinefleisch bzw. mit Gelatine vom Schwein"},
    "3": {"name": "Alkohol", "type": "additive", "description": "Alkohol"},
    "4": {"name": "Geschmacksverstärker", "type": "additive", "description": "Geschmacksverstärker"},
    "5": {"name": "gewachst", "type": "additive", "description": "gewachst"},
    "6": {"name": "konserviert", "type": "additive", "description": "konserviert"},
    "7": {"name": "Antioxidationsmittel", "type": "additive", "description": "Antioxidationsmittel"},
    "8": {"name": "Farbstoff", "type": "additive", "description": "Farbstoff"},
    "9": {"name": "Phosphat", "type": "additive", "description": "Phosphat"},
    "10": {"name": "geschwärzt", "type": "additive", "description": "geschwärzt"},
    "12": {"name": "Phenylalaninquelle", "type": "additive", "description": "enthält eine Phenylalaninquelle"},
    "13": {"name": "Süßungsmittel", "type": "additive", "description": "Süßungsmittel"},
    "14": {"name": "fein_zerkleinertes_fleisch", "type": "additive", "description": "mit zum Teil fein zerkleinertem Fleischanteil"},
    "16": {"name": "koffeinhaltig", "type": "additive", "description": "koffeinhaltig"},
    "17": {"name": "chininhaltig", "type": "additive", "description": "chininhaltig"},
    "19": {"name": "geschwefelt", "type": "additive", "description": "geschwefelt"},
    "20": {"name": "abführend_wirken", "type": "additive", "description": "kann abführend wirken"},
    
    # Allergens
    "21": {"name": "Gluten", "type": "allergen", "description": "Glutenhaltiges Getreide"},
    "21a": {"name": "Weizen", "type": "allergen", "description": "Weizen"},
    "21b": {"name": "Roggen", "type": "allergen", "description": "Roggen"},
    "21c": {"name": "Gerste", "type": "allergen", "description": "Gerste"},
    "21d": {"name": "Hafer", "type": "allergen", "description": "Hafer"},
    "21e": {"name": "Dinkel", "type": "allergen", "description": "Dinkel"},
    "21f": {"name": "Kamut", "type": "allergen", "description": "Kamut"},
    "22": {"name": "Krebstiere", "type": "allergen", "description": "Krebstiere"},
    "23": {"name": "Eier", "type": "allergen", "description": "Eier"},
    "24": {"name": "Fisch", "type": "allergen", "description": "Fisch"},
    "25": {"name": "Erdnüsse", "type": "allergen", "description": "Erdnüsse"},
    "26": {"name": "Schalenfrüchte", "type": "allergen", "description": "Schalenfrüchte"},
    "26a": {"name": "Mandeln", "type": "allergen", "description": "Mandeln"},
    "26b": {"name": "Haselnuss", "type": "allergen", "description": "Haselnuss"},
    "26c": {"name": "Walnuss", "type": "allergen", "description": "Walnuss"},
    "26d": {"name": "Kaschunuss", "type": "allergen", "description": "Kaschunuss"},
    "28": {"name": "Soja", "type": "allergen", "description": "Soja"},
    "29": {"name": "Senf", "type": "allergen", "description": "Senf"},
    "30": {"name": "Milch", "type": "allergen", "description": "Milch und Milchprodukte (einschließlich Laktose)"},
    "31": {"name": "Schalenfrüchte", "type": "allergen", "description": "Schalenfrüchte z.B. Mandeln, Haselnüsse, Walnüsse etc."},
    "32": {"name": "Sellerie", "type": "allergen", "description": "Sellerie"},
    "33": {"name": "Senf", "type": "allergen", "description": "Senf"},
    "34": {"name": "Sesam", "type": "allergen", "description": "Sesam"},
    "35": {"name": "Schwefeldioxid", "type": "allergen", "description": "Schwefeldioxid und Sulfite"},
    "36": {"name": "Lupinen", "type": "allergen", "description": "Lupinen"},
    "37": {"name": "Weichtiere", "type": "allergen", "description": "Weichtiere"},
}

# Traffic light mapping
TRAFFIC_LIGHT_MAP = {
    "ampel_gruen": {"name": "Grün", "description": "Die beste Wahl – je öfter, desto besser"},
    "ampel_gelb": {"name": "Gelb", "description": "Eine gute Wahl – immer mal wieder"},
    "ampel_rot": {"name": "Rot", "description": "Eher selten – am besten mit Grün kombinieren"},
}

# Dietary icon mapping
DIETARY_ICON_MAP = {
    "1.png": {"name": "Vegetarisch", "description": "Gerichte werden ohne Fisch- und Fleischzutaten zubereitet"},
    "15.png": {"name": "Vegan", "description": "Gericht ist aus ausschließlich pflanzlichen Rohstoffen zubereitet"},
    # Add more icons as needed from actual HTML analysis
    "18.png": {"name": "Bio", "description": "Biologisch erzeugte Lebensmittel"},
    "38.png": {"name": "Klimaessen", "description": "Klimafreundliches Gericht"},
    "41.png": {"name": "Regionales Gericht", "description": "Regionale Zutaten verwendet"},
    "43.png": {"name": "Fair Trade", "description": "Fair-Trade-Zutaten verwendet"},
}


@dataclass
class Pricing:
    """Structured pricing information"""
    raw: str
    student: Optional[float] = None
    employee: Optional[float] = None
    guest: Optional[float] = None
    is_available: bool = True


@dataclass
class NutritionInfo:
    """Nutritional information"""
    traffic_light: Optional[str] = None
    traffic_light_description: Optional[str] = None


@dataclass
class DietaryInfo:
    """Dietary labels and restrictions"""
    labels: List[str]
    vegetarian: bool = False
    vegan: bool = False


@dataclass
class AllergenInfo:
    """Allergen and additive information"""
    codes: List[str]
    readable: List[str]
    additives: List[str]
    allergens: List[str]


@dataclass
class Meal:
    """Complete meal information"""
    category: str
    name: str
    pricing: Pricing
    nutrition: NutritionInfo
    dietary: DietaryInfo
    allergens: AllergenInfo


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
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            path,
            query,
            parts.fragment,
        )
    )


def safe_get_text(element: Optional[Tag], default: str = "") -> str:
    """Safely extract text from a BeautifulSoup element"""
    if element is None:
        return default
    return element.get_text(strip=True)


def safe_get_attribute(element: Optional[Tag], attribute: str, default: str = "") -> str:
    """Safely extract attribute from a BeautifulSoup element"""
    if element is None:
        return default
    value = element.get(attribute, default) or default
    return str(value) if value else default


def parse_price_string(price_text: str) -> Pricing:
    """Parse price string and extract individual price tiers"""
    if not price_text or not price_text.strip():
        return Pricing(raw="", is_available=False)
    
    # Remove € symbol and whitespace
    cleaned = re.sub(r'[€\s]', '', price_text.strip())
    
    if not cleaned:
        return Pricing(raw=price_text, is_available=False)
    
    student = employee = guest = None
    
    try:
        # Split by / to get individual prices
        price_parts = [p.strip() for p in cleaned.split('/') if p.strip()]
        
        if len(price_parts) >= 1:
            student = float(price_parts[0].replace(',', '.'))
        if len(price_parts) >= 2:
            employee = float(price_parts[1].replace(',', '.'))
        if len(price_parts) >= 3:
            guest = float(price_parts[2].replace(',', '.'))
            
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to parse price '{price_text}': {e}")
        return Pricing(raw=price_text, is_available=True)
    
    return Pricing(
        raw=price_text,
        student=student,
        employee=employee, 
        guest=guest,
        is_available=True
    )


def parse_allergen_codes(allergen_string: str) -> AllergenInfo:
    """Parse allergen codes and provide readable descriptions"""
    if not allergen_string:
        return AllergenInfo(codes=[], readable=[], additives=[], allergens=[])
    
    # Split codes and clean them
    codes = [code.strip() for code in allergen_string.split(',') if code.strip()]
    
    readable = []
    additives = []
    allergens = []
    
    for code in codes:
        if code in ALLERGEN_ADDITIVES:
            info = ALLERGEN_ADDITIVES[code]
            readable.append(info["description"])
            if info["type"] == "additive":
                additives.append(info["name"])
            elif info["type"] == "allergen":
                allergens.append(info["name"])
        else:
            readable.append(code)
            # Unknown codes - categorize as allergen by default
            allergens.append(code)
    
    return AllergenInfo(
        codes=codes,
        readable=readable,
        additives=additives,
        allergens=allergens
    )


def parse_icons(meal_element: Tag) -> Tuple[NutritionInfo, DietaryInfo]:
    """Parse icons to extract nutrition and dietary information"""
    nutrition = NutritionInfo()
    dietary_labels = []
    is_vegetarian = False
    is_vegan = False
    
    icons = meal_element.find_all("img", class_="splIcon")
    
    for icon in icons:
        src = safe_get_attribute(icon, "src", "")
        alt = safe_get_attribute(icon, "alt", "")
        
        # Check for traffic light icons
        traffic_light_found = False
        for traffic_key, traffic_info in TRAFFIC_LIGHT_MAP.items():
            if traffic_key in src:
                nutrition.traffic_light = traffic_info["name"]
                nutrition.traffic_light_description = traffic_info["description"]
                traffic_light_found = True
                break
        
        if not traffic_light_found:
            # Check for dietary icons
            icon_name = src.split('/')[-1]  # Extract filename
            if icon_name in DIETARY_ICON_MAP:
                dietary_info = DIETARY_ICON_MAP[icon_name]
                dietary_labels.append(dietary_info["name"])
                
                if dietary_info["name"] == "Vegetarisch":
                    is_vegetarian = True
                elif dietary_info["name"] == "Vegan":
                    is_vegan = True
                    is_vegetarian = True  # Vegan implies vegetarian
    
    dietary = DietaryInfo(
        labels=dietary_labels,
        vegetarian=is_vegetarian,
        vegan=is_vegan
    )
    
    return nutrition, dietary


def parse_meal(meal_element: Tag) -> Optional[Meal]:
    """Parse a single meal element"""
    try:
        # Extract meal name
        name_element = meal_element.find("span", class_="bold")
        if not name_element:
            logger.warning("No name element found in meal")
            return None
            
        name = safe_get_text(name_element)
        if not name:
            logger.warning("Empty meal name found")
            return None
        
        # Extract allergen codes
        allergen_codes_raw = safe_get_attribute(meal_element, "data-kennz", "")
        allergens = parse_allergen_codes(allergen_codes_raw)
        
        # Extract pricing information
        price_element = meal_element.find("div", class_="text-right")
        price_text = safe_get_text(price_element) if price_element else ""
        pricing = parse_price_string(price_text)
        
        # Parse icons for nutrition and dietary info
        nutrition, dietary = parse_icons(meal_element)
        
        return Meal(
            category="",  # Will be filled by parent parsing
            name=name,
            pricing=pricing,
            nutrition=nutrition,
            dietary=dietary,
            allergens=allergens
        )
        
    except Exception as e:
        logger.error(f"Error parsing meal element: {e}")
        return None


app = typer.Typer()
console = Console()
MENU_URL = "https://www.stw.berlin/mensen/einrichtungen/humboldt-universität-zu-berlin/mensa-hu-süd.html"


def fetch_page(url: str) -> str:
    """Fetch and return page content with error handling"""
    normalized = normalize_url(url)
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching menu...", total=None)
            
            resp = requests.get(normalized, timeout=10, headers=HEADERS)
            resp.raise_for_status()
            
            progress.update(task, description="Menu fetched successfully!")
            
        return resp.text
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching {url}")
        raise typer.Exit(code=1)
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while fetching {url}")
        raise typer.Exit(code=1)
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error while fetching {url}: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error while fetching {url}: {e}")
        raise typer.Exit(code=1)


def parse_menu(html: str) -> List[Meal]:
    """Parse the complete menu from HTML"""
    soup = BeautifulSoup(html, "html.parser")

    speiseplan = soup.find("div", id="speiseplan")
    if not speiseplan:
        raise RuntimeError("div#speiseplan not found")

    meals = []

    for group in speiseplan.find_all("div", class_="splGroupWrapper", recursive=False):
        # Extract category name
        group_name_element = group.find("div", class_="splGroup")
        if not group_name_element:
            logger.warning("No category name found in group wrapper")
            continue

        category = safe_get_text(group_name_element)

        # Process meals in this category
        meal_elements = group.find_all("div", class_="splMeal", recursive=False)
        
        for meal_element in meal_elements:
            meal = parse_meal(meal_element)
            if meal:
                meal.category = category  # Set category from parent
                meals.append(meal)

    return meals


def format_price(pricing: Pricing, show_tier: str = "student") -> str:
    """Format price for display based on tier preference"""
    if not pricing.is_available:
        return ""
    
    if show_tier == "student" and pricing.student is not None:
        return f"€{pricing.student:.2f}"
    elif show_tier == "employee" and pricing.employee is not None:
        return f"€{pricing.employee:.2f}"
    elif show_tier == "guest" and pricing.guest is not None:
        return f"€{pricing.guest:.2f}"
    else:
        return pricing.raw


def create_meal_table(meals: List[Meal], show_allergens: bool = True, 
                     show_prices: bool = True, price_tier: str = "student",
                     show_nutrition: bool = True, show_dietary: bool = True) -> Table:
    """Create a formatted table with meal information"""
    table = Table(show_header=True, header_style="bold green")
    
    # Determine which columns to show
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
        columns = [
            meal.category,
            meal.name,
        ]
        
        if show_dietary:
            dietary_text = ", ".join(meal.dietary.labels) if meal.dietary.labels else ""
            columns.append(dietary_text)
        
        if show_nutrition:
            nutrition_text = meal.nutrition.traffic_light or ""
            columns.append(nutrition_text)
        
        if show_allergens:
            allergen_text = ", ".join(meal.allergens.codes) if meal.allergens.codes else ""
            columns.append(allergen_text)
        
        if show_prices:
            price_text = format_price(meal.pricing, price_tier)
            columns.append(price_text)
        
        table.add_row(*columns)

    return table


def print_summary_stats(meals: List[Meal]):
    """Print summary statistics about the parsed menu"""
    console.print("\n[bold blue]Summary Statistics:[/]")
    
    categories = set(meal.category for meal in meals)
    vegetarian_count = sum(1 for meal in meals if meal.dietary.vegetarian)
    vegan_count = sum(1 for meal in meals if meal.dietary.vegan)
    
    console.print(f"• Total meals: {len(meals)}")
    console.print(f"• Categories: {', '.join(sorted(categories))}")
    console.print(f"• Vegetarian options: {vegetarian_count}")
    console.print(f"• Vegan options: {vegan_count}")
    
    # Traffic light distribution
    traffic_lights = {}
    for meal in meals:
        light = meal.nutrition.traffic_light or "Unknown"
        traffic_lights[light] = traffic_lights.get(light, 0) + 1
    
    if traffic_lights:
        console.print("• Nutrition distribution:")
        for light, count in traffic_lights.items():
            console.print(f"  - {light}: {count}")


@app.command()
def scrape(
    url: str = typer.Option(MENU_URL, "--url", "-u", help="URL to scrape"),
    show_allergens: bool = typer.Option(True, "--allergens/--no-allergens", help="Show allergen information"),
    show_prices: bool = typer.Option(True, "--prices/--no-prices", help="Show price information"),
    price_tier: str = typer.Option("student", "--price-tier", help="Price tier to show (student/employee/guest)"),
    show_nutrition: bool = typer.Option(True, "--nutrition/--no-nutrition", help="Show nutrition traffic lights"),
    show_dietary: bool = typer.Option(True, "--dietary/--no-dietary", help="Show dietary labels"),
    summary: bool = typer.Option(False, "--summary", "-s", help="Show summary statistics"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
):
    """
    Scrape a Mensa menu from the given URL and display it with customizable options.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    try:
        console.print(f"[blue]Fetching menu from:[/] {url}")
        html = fetch_page(url)

        console.print("[blue]Parsing menu...[/]")
        meals = parse_menu(html)

        if not meals:
            console.print("[yellow]No dishes found — maybe the structure differs?[/]")
            return

        console.print(f"[green]Successfully parsed {len(meals)} meals![/]")
        
        # Display the table
        table = create_meal_table(
            meals, 
            show_allergens=show_allergens,
            show_prices=show_prices,
            price_tier=price_tier,
            show_nutrition=show_nutrition,
            show_dietary=show_dietary
        )
        console.print(table)
        
        # Show summary if requested
        if summary:
            print_summary_stats(meals)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
