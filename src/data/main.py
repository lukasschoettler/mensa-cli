import sqlite3

from common.logger import log
from common.models import MensaCreate
from common.providers.__init__ import SITES
from data.ingest import ingest_fetches
from data.processing import FetchProcessor
from data.queries import (
    FetchRepository,
    MealRepository,
    MensaRepository,
    MenuRepository,
)
from data.schema import DatabaseSchema

try:
    connection = sqlite3.connect("db/mensa.db")
except Exception as e:
    e.add_note("Hint: Is the database mounted correctly?")
    raise e

assert SITES.__len__() > 0
connection.row_factory = sqlite3.Row
setup = DatabaseSchema(connection)
setup.ensure_all()

mensas = MensaRepository(connection)
for key, site in SITES.items():
    try:
        key = site.key
    except Exception as e:
        log.info(
            f"Couldn't extract key from SITES for key: {key} with site: {site}. {e}"
        )
        continue

    try:
        url = site.url
    except Exception as e:
        log.info(f"Couldn't extract URL from SITES for {key}. {e}")
        continue

    try:
        name = site.name
    except Exception as e:
        log.info(f"Couldn't extract name from SITES for {key}. {e}")
        continue

    try:
        provider = site.provider
    except Exception as e:
        log.info(f"Couldn't extract provider from SITES for {key}. {e}")
        continue

    try:
        city = site.city
    except Exception as e:
        log.info(f"Couldn't extract city from SITES for {key}. {e}")
        continue

    mensas.upsert(mensa=MensaCreate(key, name, provider, url, city))

ingest_fetches(connection)

fetch_repo = FetchRepository(connection)

fetches = fetch_repo.select_unparsed()

fetch_processor = FetchProcessor(fetches)

results = fetch_processor.process_all()

if not fetches:
    log.info("No unprocessed fetches in database found")
else:
    for result in results:
        with connection as conn:
            menu_repo = MenuRepository(conn)
            meal_repo = MealRepository(conn)

            menu_after = menu_repo.insert(result[0])
            for meal in result[1]:
                meal_after = meal_repo.upsert(meal)
                menu_repo.insert_meal_junction(menu_after.id, meal_after.id)

connection.commit()
