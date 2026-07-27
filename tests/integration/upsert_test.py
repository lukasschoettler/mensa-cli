import sqlite3
from data.main import upsert_processed_fetches 
from data.schema import DatabaseSchema
from data.ingest import ingest_fetches
from pathlib import Path
from common.providers import MENSAS
from data.queries import (
    MensaRepository,
)
from common.models import MensaCreate

# ToDo: make provider agnostic
def url_to_fixture(url: str) -> str:
    path = url.replace("https://www.stw.berlin/mensen/einrichtungen/", "", 1)
    path = path.replace("/", "_")
    return path

def mock_fetcher(url, *args, **kwargs ) -> str:
    # print("received URL: ", url)
    path = url_to_fixture(url)
    fullpath = Path("tests/integration/fixtures/") / path
    with open(fullpath) as file:
        html = file.read()
    return html

def setup_mock_db(connection):
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA journal_mode=WAL;")

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


def test_meal_deduplication():
    """
    test, whether repeated ingestion and processing of identical fetches leads to duplicated meals
    """
    connection = sqlite3.connect(":memory:")
    setup_mock_db(connection)

    ingest_fetches(connection, mock_fetcher)
    upsert_processed_fetches(connection)

    cursor = connection.cursor()
    cursor.execute("""/*SQL*/
SELECT COUNT(*)
FROM meals;
                       """)
    meals_first_process =  cursor.fetchone()[0]

    ingest_fetches(connection, mock_fetcher)
    upsert_processed_fetches(connection)

    cursor.execute("""/*SQL*/
SELECT COUNT(*)
FROM meals;
                       """)
    meals_second_process =  cursor.fetchone()[0]

    assert meals_first_process == meals_second_process


def test_menu_deduplication():
    """
    test, whether repeated ingestion and processing of identical fetches leads to duplicated menus 
    """
    connection = sqlite3.connect(":memory:")
    setup_mock_db(connection)

    ingest_fetches(connection, mock_fetcher)
    upsert_processed_fetches(connection)

    cursor = connection.cursor()
    cursor.execute("""/*SQL*/
SELECT COUNT(*)
FROM menus;
                       """)
    menus_first_process =  cursor.fetchone()[0]

    ingest_fetches(connection, mock_fetcher)
    upsert_processed_fetches(connection)

    cursor.execute("""/*SQL*/
SELECT COUNT(*)
FROM menus;
                       """)
    menus_second_process =  cursor.fetchone()[0]

    assert menus_first_process == menus_second_process
