import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv(verbose=True)

        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.crawl: str = os.getenv("CRAWL", "TRUE").upper()
        self.db_name: str = os.getenv("DB_NAME", "").lower()

    def __post_init__(self):
        assert self.db_name != "", "DB_NAME must be provided as an environment variable"
