import os
import sqlite3

from common.logger import log
from common.models import MealCreate, MensaCreate
from common.providers import MENSAS
from data.config import Config
from data.ingest import ingest_fetches
from data.processing import FetchProcessor
from data.queries import (
    FetchRepository,
    MealRepository,
    MensaRepository,
    MenuRepository,
)
from data.schema import DatabaseSchema

config = Config()

try:
    connection = sqlite3.connect(f"db/{config.db_name}.db")
except Exception as e:
    e.add_note("Hint: Is the database mounted correctly?")
    raise e

assert len(MENSAS) > 0
connection.row_factory = sqlite3.Row
schema = DatabaseSchema(connection)
schema.ensure_all()

mensa_repo = MensaRepository(connection)
for key, site in MENSAS:
    mensa_repo.upsert(
        mensa=MensaCreate(
            key=site.key,
            name=site.name,
            provider=site.provider,
            url=site.url,
            city=site.city,
        )
    )

if config.crawl == "FALSE":
    pass
else:
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
                menu_repo.insert_meal_junction(
                    menu_after.id,
                    meal_after.id,
                    MealCreate(
                        meal.name,
                        meal.mensa_key,
                        meal.price_student,
                        meal.price_employee,
                        meal.price_guest,
                    ),
                )

connection.commit()
