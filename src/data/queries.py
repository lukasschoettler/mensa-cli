import sqlite3
from typing import Dict
from uuid import UUID


def ensure_table_fetches(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS fetches (
  id TEXT PRIMARY KEY,
  html TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  url TEXT NOT NULL,
  mensa_key TEXT NOT NULL
)
    """)
    return None


def insert_fetches(
    cursor: sqlite3.Cursor, html: str, url: str, mensa_key: str, id: UUID
) -> None:

    id_str = str(id)

    cursor.execute(
        """/*SQL*/
INSERT INTO
  fetches (id, html, fetched_at, url, mensa_key)
VALUES
  (?, ?, datetime ("now"), ?, ?)
  """,
        (id_str, html, url, mensa_key),
    )


def ensure_table_mensas(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS mensas (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL,
  city TEXT NOT NULL
)""")


def update_mensas(
    cursor: sqlite3.Cursor, key: str, name: str, url: str, city: str
) -> None:
    cursor.execute(
        """/*SQL*/
INSERT INTO
  mensas (key, name, url, city)
VALUES
  (?, ?, ?, ?) ON CONFLICT (key) DO
UPDATE
SET
  name = excluded.name,
  url = excluded.url,
  city = excluded.city
  """,
        (key, name, url, city),
    )


def ensure_table_menus(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS menus (
  id TEXT PRIMARY KEY,
  fetch_id,
  timestamp TEXT NOT NULL,
  mensa_key TEXT NOT NULL,
  FOREIGN KEY (fetch_id) REFERENCES fetches (id),
  FOREIGN KEY (mensa_key) REFERENCES mensas (key)
)
  """)


def ensure_table_meals(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS meals (
  id INTEGER PRIMARY KEY,
  name TEXT,
  mensa_key TEXT,
  FOREIGN KEY (mensa_key) REFERENCES mensas (key)
)
    """)


def ensure_table_menus_meals(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""/*SQL*/
CREATE TABLE menu_meals (
    menu_id INTEGER NOT NULL,
    meal_id INTEGER NOT NULL,
    PRIMARY KEY (menu_id, meal_id),
    FOREIGN KEY (menu_id) REFERENCES menus(id),
    FOREIGN KEY (meal_id) REFERENCES meals(id)
)
    )
                   """)


def get_fetches(cursor: sqlite3.Cursor) -> Dict:
    result = cursor.execute("""/*SQL*/
SELECT
  *
FROM
  fetches
                   """)
    fetches = dict(result.fetchall())
    print(fetches)
    return fetches
