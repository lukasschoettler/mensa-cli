import sqlite3
from uuid import uuid4

from common.http import fetch_html
from common.providers.__init__ import SITES
from data.queries import insert_fetches


def ingest_fetches(cursor: sqlite3.Cursor) -> None:

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

        fetch_id = uuid4()

        try:
            insert_fetches(cursor, html, url, mensa_key, fetch_id)
            print(f"Saved raw html for {mensa_key} to database")
        except Exception as e:
            print(f"Failed to insert raw html into database: {e}")
