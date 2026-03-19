import sqlite3
from typing import Counter, Dict, List, Tuple, TypedDict
from uuid import uuid4

from common.models import Meal
from common.providers import SITES
from common.providers.types import MensaSite, ParseResult

# from common.http import fetch_html
# from common.providers.__init__ import SITES
from data.queries import (
    get_fetches,
    insert_meal,
    insert_menu,
    insert_menu_meal_junction,
)


class StructuredFetch(TypedDict):
    id: str
    html: str
    timestamp: str
    url: str
    mensa_key: str


def make_fetch_structured(fetch: Tuple[str, str, str, str, str]) -> StructuredFetch:

    structured_fetch: StructuredFetch = {
        "id": fetch[0],
        "html": fetch[1],
        "timestamp": fetch[2],
        "url": fetch[3],
        "mensa_key": fetch[4],
    }
    return structured_fetch


def parse_menu(
    sites: Dict[str, MensaSite], structured_fetch: StructuredFetch
) -> ParseResult:

    site = sites[structured_fetch["mensa_key"]]
    parser = site.parser

    menu = parser(structured_fetch["html"])
    return menu


def process_fetch(
    cursor: sqlite3.Cursor,
    sites: Dict[str, MensaSite],
    fetch: Tuple[str, str, str, str, str],
) -> None:
    structured_fetch = make_fetch_structured(fetch)
    print(
        f"Processing fetch {structured_fetch["id"]} from {structured_fetch["timestamp"]} of {structured_fetch["mensa_key"]}"
    )
    menu_id = str(uuid4())
    fetch_id = structured_fetch["id"]
    # timestamp = structured_fetch[
    #     "timestamp"
    # ]  # This is redundant if fetch timestamp is used
    mensa_key = structured_fetch["mensa_key"]

    try:
        insert_menu(cursor, menu_id, fetch_id, mensa_key)
    except Exception as e:
        raise e
        # print(f"An exception occured while trying to insert menu into database: {e}")

    menu = parse_menu(sites, structured_fetch)
    for meal in menu.meals:
        meal_id = str(uuid4())
        name = meal.name
        try:
            meal_id_return = insert_meal(cursor, meal_id, name, mensa_key)
            if meal_id == meal_id_return:
                print(f"Inserted Meal {name} into database")
            else:
                print(
                    f"Meal {name} already present in database with id: {meal_id_return}"
                )
        except Exception as e:
            print(
                f"An exception occured while trying to insert meal {name} into database: {e}"
            )
            continue
        try:
            insert_menu_meal_junction(cursor, menu_id, meal_id_return)
            print(f"Inserted junction for meal {name} and menu {menu_id}")
        except Exception as e:
            print(
                f"An error occured while trying to insert junction for meal {name} and menu {menu_id}: {e}"
            )
