import json
from typing import TypedDict
from storage.database_manager import ElementsDatabaseManager


class Element(TypedDict):
    text: str
    emoji: str


def load_json(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def process(file_path: str, db_path: str):
    elements_db_manager = ElementsDatabaseManager(db_path)

    data = load_json(file_path)

    elements: list[Element] = data["elements"]

    len_elements = len(elements)

    number_of_batches = 5000
    batch_size = len_elements // number_of_batches

    for i in range(0, len_elements, batch_size):
        print(f"Processing batch {i // batch_size}")
        element_batch = elements[i : i + batch_size]
        try:
            elements_db_manager.bulk_add_elements(
                [(element["text"], element["emoji"]) for element in element_batch]
            )
        except Exception:
            pass
