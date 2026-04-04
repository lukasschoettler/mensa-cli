import logging
import sys

from data.config import Config


def setup_logger(name: str = "app"):

    config = Config()
    level = config.log_level

    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


log = setup_logger()
