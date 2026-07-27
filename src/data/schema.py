from sqlite3 import Connection


class DatabaseSchema:
    def __init__(self, conn: Connection):
        self.conn = conn

    def ensure_table_mensas(self) -> None:
        self.conn.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS mensas (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  provider TEXT NOT NULL,
  url TEXT NOT NULL,
  city TEXT NOT NULL
);
        """)

    def ensure_table_fetches(self) -> None:
        self.conn.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS fetches (
  id INTEGER PRIMARY KEY,
  html TEXT NOT NULL,
  timestamp DATETIME NOT NULL,
  url TEXT NOT NULL,
  mensa_key TEXT NOT NULL
);
        """)

    def ensure_table_menus(self) -> None:
        self.conn.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS menus (
  id INTEGER PRIMARY KEY,
  fetch_id INTEGER NOT NULL,
  timestamp TEXT NOT NULL,
  mensa_key TEXT NOT NULL,
  FOREIGN KEY (fetch_id) REFERENCES fetches (id),
  FOREIGN KEY (mensa_key) REFERENCES mensas (key)
);
        """)

    def ensure_table_meals(self) -> None:
        self.conn.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS meals (
  id INTEGER PRIMARY KEY,
  timestamp TEXT NOT NULL,
  name TEXT NOT NULL,
  mensa_key TEXT NOT NULL,
  vegetarian INTEGER NOT NULL DEFAULT -1,
  vegan INTEGER NOT NULL DEFAULT -1,
  FOREIGN KEY (mensa_key) REFERENCES mensas (key),
  UNIQUE (name, mensa_key, vegetarian, vegan)
);
        """)

    def ensure_table_menus_meals(self) -> None:
        self.conn.execute("""/*SQL*/
CREATE TABLE IF NOT EXISTS menus_meals (
  menu_id INTEGER NOT NULL,
  meal_id INTEGER NOT NULL,
  price_student REAL,
  price_guest REAL,
  price_employee REAL,
  PRIMARY KEY (menu_id, meal_id),
  FOREIGN KEY (menu_id) REFERENCES menus (id),
  FOREIGN KEY (meal_id) REFERENCES meals (id)
);
        """)

    def ensure_all(self) -> None:
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.ensure_table_mensas()
        self.ensure_table_fetches()
        self.ensure_table_menus()
        self.ensure_table_meals()
        self.ensure_table_menus_meals()
