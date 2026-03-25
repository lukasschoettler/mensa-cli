import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def setup_logger(name: str = "app", level: int | None = None):
    logger = logging.getLogger(name)

    if not logger.handlers:
        env_level = os.getenv("LOG_LEVEL", "INFO").upper()
        resolved_level = level or getattr(logging, env_level, logging.INFO)

        logger.setLevel(resolved_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


log = setup_logger()
