import sqlite3
from datetime import datetime as dt

from common.http import fetch_html
from common.providers.__init__ import SITES
from common.providers.types import MensaSite

connection = sqlite3.connect("db/mensa.db")

db = connection.cursor()

db.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS menus_raw (
  html TEXT,
  date TEXT,
  url TEXT,
  mensa_key TEXT,
  status TEXT
);
""")

assert SITES.__len__() > 0


def resolve_site(key: str) -> MensaSite:
    try:
        return SITES[key]
    except KeyError as exc:
        raise ValueError("Key doesn't exist in SITES") from exc


for key, site in SITES.items():
    try:
        mensa_key = site.key
    except:
        print(
            f"Couldn't extract key from SITES for key: {key} with site: {site}. SKIPPING"
        )
        continue

    try:
        url = site.url
    except:
        print(f"Couldn't extract URL from SITES for {mensa_key}. SKIPPING")
        continue

    date_time = dt.now().isoformat()

    try:
        html = fetch_html(url)
    except:
        print(f"Couldn't fetch html for {mensa_key} at {url}")
        continue

    try:
        db.execute(
            """/*SQL*/
INSERT INTO
  menus_raw (html, date, url, mensa_key)
VALUES
  (?, ?, ?, ?)
               """,
            (
                html,
                date_time,
                url,
                mensa_key,
            ),
        )
        print(f"Saved raw html for {mensa_key} to database")
    except:
        print("Failed to insert raw html into database")

connection.commit()
