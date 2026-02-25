import sqlite3

print("hello docker")

db = sqlite3.connect("db/mensa.db")

db.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS menus_raw (
  html TEXT,
  date TEXT,
  url TEXT,
  mensa_key TEXT,
  status TEXT
);
""")

result = db.execute("""/*SQL*/
SELECT
  *
FROM
  menus_raw;
""")


print(result)
