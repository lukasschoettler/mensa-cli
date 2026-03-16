import sqlite3

# from common.http import fetch_html
# from common.providers.__init__ import SITES
from data.queries import get_fetches

# from uuid import uuid4


def parse_fetches(cursor: sqlite3.Cursor) -> None:
    get_fetches(cursor)
