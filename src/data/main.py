import sqlite3

from common.providers.__init__ import SITES
from data.ingest import ingest_fetches
from data.parse import parse_fetches
from data.queries import (
    ensure_table_fetches,
    ensure_table_meals,
    ensure_table_mensas,
    ensure_table_menus,
    update_mensas,
)

try:
    connection = sqlite3.connect("db/mensa.db")
except Exception as e:
    e.add_note("Hint: Is the database mounted correctly?")
    raise e

cursor = connection.cursor()

# def validate_sites(SITES) -> None:

ensure_table_mensas(cursor)

assert SITES.__len__() > 0
for key, site in SITES.items():
    try:
        key = site.key
    except:
        print(f"Couldn't extract key from SITES for key: {key} with site: {site}")
        continue

    try:
        url = site.url
    except:
        print(f"Couldn't extract URL from SITES for {key}")
        continue

    try:
        name = site.name
    except:
        print(f"Couldn't extract name from SITES for {key}")
        continue

    try:
        city = site.city
    except:
        print(f"Couldn't extract city from SITES for {key}")
        continue

    update_mensas(cursor, key, name, url, city)
    print(f"Upserted data for mensa: {key}")

ensure_table_fetches(cursor)
ingest_fetches(cursor)

ensure_table_menus(cursor)
ensure_table_meals(cursor)

parse_fetches(cursor)

connection.commit()
