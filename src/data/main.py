import sqlite3

from common.providers.__init__ import SITES
from data.ingest import ingest_fetches
from data.parse import process_fetch
from data.queries import (
    ensure_table_fetches,
    ensure_table_meals,
    ensure_table_mensas,
    ensure_table_menus,
    ensure_table_menus_meals,
    get_fetches_unparsed,
    update_mensas,
)

try:
    connection = sqlite3.connect("db/mensa.db")
except Exception as e:
    e.add_note("Hint: Is the database mounted correctly?")
    raise e


def ensure_wal_mode(conn: sqlite3.Connection) -> None:
    cur = conn.execute("""/*SQL*/ PRAGMA journal_mode = WAL
                       """)
    mode = cur.fetchone()[0]

    if mode.lower() != "wal":
        raise RuntimeError(f"Failed to enable WAL mode, got {mode}")


ensure_wal_mode(connection)

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
        provider = site.provider
    except:
        print(f"Couldn't extract provider from SITES for {key}")
        continue

    try:
        city = site.city
    except:
        print(f"Couldn't extract city from SITES for {key}")
        continue

    update_mensas(cursor, key, name, provider, url, city)
    print(f"Upserted data for mensa: {key}")

ensure_table_fetches(cursor)
ingest_fetches(cursor)

ensure_table_menus(cursor)
ensure_table_meals(cursor)
ensure_table_menus_meals(cursor)
fetches = get_fetches_unparsed(cursor)

if not fetches:
    print("No unprocessed fetches in database found")
else:
    print(f"{fetches.__len__()} unprocessed fetches found. Initializing proessing.")
    for fetch in fetches:
        process_fetch(cursor, SITES, fetch)

connection.commit()
