from sqlite3 import Connection, Row
from typing import List

from common.logger import log
from common.models import (
    FetchCreate,
    FetchRead,
    MealCreate,
    MealRead,
    MensaCreate,
    MenuCreate,
    MenuRead,
)


class BaseRepository:
    def __init__(self, conn: Connection):
        assert (
            conn.row_factory == Row
        ), f"Connection must use sqlite3.Row factory. Instead uses {conn.row_factory}"
        self.conn = conn


class FetchRepository(BaseRepository):
    def insert(self, fetch: FetchCreate) -> None:
        with self.conn as conn:
            conn.execute(
                """/*SQL*/
INSERT INTO
  fetches (html, timestamp, url, mensa_key)
VALUES
  (?, datetime ("now"), ?, ?)
      """,
                (fetch.html, fetch.url, fetch.mensa_key),
            )

        log.debug(f"Inserted fetch for {fetch.mensa_key}")

    def select(self) -> List[FetchRead]:
        cursor = self.conn.cursor()
        cursor.execute("""/*SQL*/
SELECT
  *
FROM
  fetches
                       """)
        return [FetchRead(**dict(row)) for row in cursor.fetchall()]

    def select_unparsed(self) -> List[FetchRead]:
        cursor = self.conn.cursor()
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
      fetch_id IS NOT NULL
  )
                           """)

        return [FetchRead(**dict(row)) for row in cursor.fetchall()]


class MensaRepository(BaseRepository):
    def upsert(self, mensa: MensaCreate) -> None:
        with self.conn as conn:
            conn.execute(
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
                (mensa.key, mensa.name, mensa.provider, mensa.url, mensa.city),
            )
        log.debug(f"Upserted mensa for {mensa.key}")


class MenuRepository(BaseRepository):
    def insert(self, menu: MenuCreate) -> MenuRead:
        with self.conn as conn:
            cursor = conn.execute(
                """/*SQL*/
INSERT INTO
  menus (fetch_id, timestamp, mensa_key)
VALUES
  (?, datetime ("now"), ?) RETURNING id,
  fetch_id,
  timestamp,
  mensa_key;
                """,
                (menu.fetch_id, menu.mensa_key),
            )
            row = cursor.fetchone()
        return_val = MenuRead(*row)
        log.debug(
            f"Inserted menu from {return_val.timestamp} of {return_val.mensa_key}"
        )
        return return_val

    def insert_meal_junction(self, menu_id: int, meal_id: int) -> None:
        with self.conn as conn:
            conn.execute(
                """/*SQL*/
INSERT INTO
  menus_meals (menu_id, meal_id)
VALUES
  (?, ?)
                       """,
                (menu_id, meal_id),
            )

        log.debug(f"Inserted menu meal junction for menu {menu_id} and meal {meal_id}")


class MealRepository(BaseRepository):
    def upsert(self, meal: MealCreate) -> MealRead:
        with self.conn as conn:
            cursor = conn.execute(
                """/*SQL*/ INSERT
OR IGNORE INTO meals (name, timestamp, mensa_key)
VALUES
  (?, datetime ('now'), ?)
                """,
                (
                    meal.name,
                    meal.mensa_key,
                ),
            )

            was_inserted = cursor.rowcount == 1

            row = conn.execute(
                """/*SQL*/
SELECT
  *
FROM
  meals
WHERE
  name = ?
  AND mensa_key = ?
                """,
                (
                    meal.name,
                    meal.mensa_key,
                ),
            ).fetchone()

        if row is None:
            raise RuntimeError("Expected a meal row after upsert")

        return_val = MealRead(**dict(row))

        if was_inserted:
            log.debug(f"Inserted new meal with id {return_val.id}")
        else:
            log.debug(f"Meal already existed with id {return_val.id}")

        return return_val
