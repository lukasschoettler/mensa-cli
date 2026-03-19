import sqlite3
from typing import List, Tuple


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


def insert_fetch(
    cursor: sqlite3.Cursor, html: str, url: str, mensa_key: str, fetch_id: str
) -> None:
    cursor.execute(
        """/*SQL*/
INSERT INTO
  fetches (id, html, fetched_at, url, mensa_key)
VALUES
  (?, ?, datetime ("now"), ?, ?)
  """,
        (fetch_id, html, url, mensa_key),
    )


def ensure_table_mensas(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS mensas (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  provider TEXT NOT NULL,
  url TEXT NOT NULL,
  city TEXT NOT NULL
)""")


def update_mensas(
    cursor: sqlite3.Cursor, key: str, name: str, provider: str, url: str, city: str
) -> None:
    cursor.execute(
        """/*SQL*/
INSERT INTO
  mensas (key, name, provider, url, city)
VALUES
  (?, ?, ?, ?, ?) ON CONFLICT (key) DO
UPDATE
SET
  name = excluded.name,
  provider = excluded.provider,
  url = excluded.url,
  city = excluded.city
  """,
        (key, name, provider, url, city),
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


def insert_menu(cursor: sqlite3.Cursor, id: str, fetch_id: str, mensa_key: str) -> None:
    cursor.execute(
        """/*SQL*/
INSERT INTO
  menus (id, fetch_id, timestamp, mensa_key)
VALUES
  (?, ?, datetime ("now"), ?)
""",
        (
            id,
            fetch_id,
            mensa_key,
        ),
    )


def ensure_table_meals(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS meals (
  id TEXT PRIMARY KEY,
  name TEXT,
  mensa_key TEXT,
  FOREIGN KEY (mensa_key) REFERENCES mensas (key),
  UNIQUE (name, mensa_key)
)
    """)


# INSERT INTO my_table (id, name, email)
# VALUES (?, ?, ?)
# ON CONFLICT(name, email) DO UPDATE SET id=id
# RETURNING id;


def insert_meal(cursor: sqlite3.Cursor, id: str, name: str, mensa_key: str) -> str:
    cursor.execute(
        """/*SQL*/
INSERT INTO
  meals (id, name, mensa_key)
VALUES
  (?, ?, ?) ON CONFLICT (name, mensa_key) DO
UPDATE
SET
  id = id RETURNING id;
""",
        (
            id,
            name,
            mensa_key,
        ),
    )

    row = cursor.fetchone()
    if row is None:
        raise RuntimeError("Expected a row from RETURNING")

    return row[0]


def ensure_table_menus_meals(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS menus_meals (
  menu_id INTEGER NOT NULL,
  meal_id INTEGER NOT NULL,
  PRIMARY KEY (menu_id, meal_id),
  FOREIGN KEY (menu_id) REFERENCES menus (id),
  FOREIGN KEY (meal_id) REFERENCES meals (id)
)""")


def insert_menu_meal_junction(
    cursor: sqlite3.Cursor, menu_id: str, meal_id: str
) -> None:
    cursor.execute(
        """/*SQL*/
INSERT INTO
  menus_meals (menu_id, meal_id)
VALUES
  (?, ?)
                   """,
        (menu_id, meal_id),
    )


def get_fetches(cursor: sqlite3.Cursor) -> List[Tuple[str, str, str, str, str]]:
    cursor.execute("""/*SQL*/
SELECT
  *
FROM
  fetches
                   """)
    fetches = cursor.fetchall()
    return fetches


def get_fetches_unparsed(
    cursor: sqlite3.Cursor,
) -> List[Tuple[str, str, str, str, str]]:
    cursor.execute("""/*SQL*/
SELECT
  *
FROM
  fetches
WHERE
  id NOT IN (
    SELECT
      fetch_id
    FROM
      menus
    WHERE
      id IS NOT NULL
  )
                   """)
    fetches = cursor.fetchall()
    return fetches
