import sqlite3
import time

print("hello docker")

db = sqlite3.connect("db/mensa.db")

result = db.execute("""/*SQL*/
                    CREATE TABLE
                    IF NOT EXISTS
                    mensa (
                        test string)
                    """)

print(result)

print("ciao docker")
