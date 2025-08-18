from typing import NamedTuple
from managerdb import DatabaseManager


class Element(NamedTuple):
    id: str
    name: str
    emoji: str


class ElementsDatabaseManager(DatabaseManager[Element]):
    def __init__(self, db_path: str):
        super().__init__(db_path, "elements")

    def add_element(self, name: str, emoji: str):
        self._insert_record({"id": name, "name": name, "emoji": emoji})

    def get_element(self, id: str) -> Element | None:
        element = self._get_record(condition="id = ?", params=(id,))
        return element

    def bulk_add_elements(self, elements: list[tuple[str, str]]):
        records = [Element(element_id, element_id, emoji) for element_id, emoji in elements]
        self._insert_records(("id", "name", "emoji"), records)

    def get_all_elements(self, offset: int = 0, limit: int = 100) -> list[Element]:
        elements = self._get_records(limit=limit, offset=offset)
        return elements


class Recipe(NamedTuple):
    id: str
    a: str
    b: str
    result: str


class RecipesDatabaseManager(DatabaseManager[Recipe]):
    def __init__(self, db_path: str):
        super().__init__(db_path, "recipes")

    def add_recipe(self, a: str, b: str, result: str):
        if a > b:
            a, b = b, a
        id = f"{a}={b}"
        self._insert_record({"id": id, "a": a, "b": b, "result": result})

    def get_all_recipes(self, result: str) -> list[Recipe] | None:
        recipes = self._get_records(condition="result = ?", params=(result,))
        return [Recipe(*recipe) for recipe in recipes] if recipes else None

    def bulk_add_recipes(self, recipes: list[tuple[str, str, str]]):
        records: list[Recipe] = []
        for a, b, result in recipes:
            if a > b:
                a, b = b, a
            id = f"{a}={b}"
            records.append(Recipe(id, a, b, result))
        print(f"Adding {len(records)} records")

        self._insert_records(("id", "a", "b", "result"), records)
