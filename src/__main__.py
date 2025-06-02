import os

import logging

from savefile_processor import process  # noqa: F401
from scrape_ib import scrape  # noqa: F401


SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
DB_PATH = os.path.join(BASE_DIR, "storage", "elements.db")
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "app.log")


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-9s %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")],
)


def main():
    OFFSET = 97_050
    LIMIT = 1_000_000 - OFFSET

    scrape(DB_PATH, OFFSET, LIMIT)


if __name__ == "__main__":
    main()
