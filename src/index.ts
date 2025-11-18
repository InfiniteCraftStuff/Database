// import os

// import logging


// from processors.emojis_processor import process as process_emojis


// SRC_DIR = os.path.dirname(os.path.abspath(__file__))
// BASE_DIR = os.path.dirname(SRC_DIR)
// DB_PATH = os.path.join(BASE_DIR, "storage", "elements.db")
// LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "app.log")


// logging.basicConfig(
//     level=logging.INFO,
//     format="[%(asctime)s] %(levelname)-9s %(message)s",
//     datefmt="%d.%m.%Y %H:%M:%S",
//     handlers=[logging.StreamHandler(), logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")],
// )


// def main():
//     process_emojis(
//         "C:/Users/roman/OneDrive/Personal/dev/InfiniteCraftStuff/scrapers/recipes/emojis.json",
//         DB_PATH,
//     )


// if __name__ == "__main__":
//     main()
