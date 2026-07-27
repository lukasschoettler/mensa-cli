import sqlite3
from typing import Callable
from common.logger import log
from common.models import FetchCreate
from common.providers import MENSAS
from data.queries import FetchRepository


def ingest_fetches(connection: sqlite3.Connection, fetcher: Callable) -> None:
    fetch_repo = FetchRepository(connection)

    for key, site in MENSAS:
        try:
            html = fetcher(site.url)
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
