import sqlite3

from common.http import fetch_html
from common.logger import log
from common.models import FetchCreate
from common.providers.__init__ import SITES
from data.queries import FetchRepository


def ingest_fetches(connection: sqlite3.Connection) -> None:

    fetch_repo = FetchRepository(connection)

    for key, site in SITES.items():
        try:
            mensa_key = site.key
        except:
            log.info(
                f"Couldn't extract key from SITES for key: {key} with site: {site}"
            )
            continue

        try:
            url = site.url
        except:
            log.info(f"Couldn't extract URL from SITES for {mensa_key}")
            continue

        try:
            html = fetch_html(url)
        except:
            log.info(f"Couldn't fetch html for {mensa_key} at {url}")
            continue

        fetch = FetchCreate(html, url, mensa_key)

        try:
            fetch_repo.insert(fetch)
        except Exception as e:
            log.info(f"Failed to insert raw html into database: {e}")
