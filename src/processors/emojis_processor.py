import json

from ..storage.database_manager import ElementsDatabaseManager


def process(file_path: str, db_path: str):
    elements_db_manager = ElementsDatabaseManager(db_path)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        data: dict[str, str] = json.loads(content)
        elements = list(data.items())
        elements_db_manager.bulk_add_elements(elements)
