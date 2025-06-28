import os

import logging


from savefile_processor import process  # type: ignore # noqa: F401
from bestrecipes_processor import process as bestrecipes_process  # type: ignore # noqa: F401
from scrape_ib import scrape  # type: ignore # noqa: F401


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
    # OFFSET = 259_495
    # LIMIT = 1_000_000 - OFFSET

    # scrape(DB_PATH, OFFSET, LIMIT)

    bestrecipes_process(
        r"C:\Users\roman\OneDrive\Personal\dev\InfiniteCraftStuff\scrapers\recipes\bestrecipes.jsonl",
        DB_PATH,
    )


if __name__ == "__main__":
    main()
