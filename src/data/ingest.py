import sqlite3
from uuid import uuid4

from common.http import fetch_html
from common.providers.__init__ import SITES


def dbwrite_raw_html(database: sqlite3.Cursor) -> None:
    assert SITES.__len__() > 0

    for key, site in SITES.items():
        try:
            mensa_key = site.key
        except:
            print(f"Couldn't extract key from SITES for key: {key} with site: {site}")
            continue

        try:
            url = site.url
        except:
            print(f"Couldn't extract URL from SITES for {mensa_key}")
            continue

        try:
            html = fetch_html(url)
        except:
            print(f"Couldn't fetch html for {mensa_key} at {url}")
            continue

        fetch_id = str(uuid4())

        try:
            database.execute(
                """/*SQL*/
INSERT INTO
  raw_html (html, date, url, mensa_key, fetch_id)
VALUES
  (?, datetime ("now"), ?, ?, ?)
                   """,
                (
                    html,
                    url,
                    mensa_key,
                    fetch_id,
                ),
            )
            print(f"Saved raw html for {mensa_key} to database")
        except Exception as e:
            print(f"Failed to insert raw html into database: {e}")
