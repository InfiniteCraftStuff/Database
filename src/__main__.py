import os

import logging

from savefile_processor import process


SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
DB_PATH = os.path.join(BASE_DIR, "storage", "elements.db")
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "app.log")


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-7s %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")],
)


def main():
    IC_DIR = r"C:\Users\roman\OneDrive\Personal\GitHub\InfiniteCraftStuff"
    SAVEFILE_REL_PATH = r"InfiniteCraftSavefiles\Savefiles\Kit\2025\01\31\23-15\infinitecraft.json"

    SAVEFILE_PATH = rf"{IC_DIR}\{SAVEFILE_REL_PATH}"

    process(SAVEFILE_PATH, DB_PATH)


if __name__ == "__main__":
    main()
