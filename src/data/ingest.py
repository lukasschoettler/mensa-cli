import sqlite3

from common.http import fetch_html
from common.logger import log
from common.models import FetchCreate
from common.providers import MENSAS
from data.queries import FetchRepository


def ingest_fetches(connection: sqlite3.Connection) -> None:
    fetch_repo = FetchRepository(connection)

    for key, site in MENSAS:
        try:
            html = fetch_html(site.url)
        except Exception as e:
            log.info(
                f"Unforeseen error: Couldn't fetch html for {site.key} at {site.url}: {e}"
            )
            continue

        if html:
            fetch = FetchCreate(html, site.url, site.key)

            try:
                fetch_repo.insert(fetch)
            except Exception as e:
                log.info(f"Failed to insert raw html into database: {e}")
