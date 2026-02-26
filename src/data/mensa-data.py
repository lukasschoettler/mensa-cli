import sqlite3

print("hello docker")

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


def show_schema():
    result = db.execute("""/*SQL*/
SELECT
  *
FROM
  sqlite_schema;
                        """)

    schema = result.fetchall()
    print(f"SCHEMA: {schema}")


show_schema()

connection.commit()


# print(result)
