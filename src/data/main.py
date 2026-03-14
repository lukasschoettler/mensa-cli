import sqlite3

from data.ingest import dbwrite_raw_html

try:
    connection = sqlite3.connect("db/mensa.db")
except Exception as e:
    e.add_note("Hint: Is the database mounted correctly?")
    raise e

db = connection.cursor()

db.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS raw_html (
  html TEXT,
  date TEXT,
  url TEXT,
  mensa_key TEXT,
  fetch_id TEXT
);
""")

dbwrite_raw_html(db)

connection.commit()
