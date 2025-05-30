import sqlite3
from typing import NamedTuple, LiteralString, Generic, TypeVar


TSchema = TypeVar("TSchema")


class DatabaseManager(Generic[TSchema]):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _execute(self, query: LiteralString, params: tuple[int | float | str | None, ...] = ()):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def _fetch(self, query: LiteralString, params: tuple[int | float | str | None, ...] = ()):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def _insert_record(
        self, table: LiteralString, *pairs: tuple[LiteralString, int | float | str | None]
    ):
        columns: tuple[LiteralString, ...]
        params: tuple[int | float | str | None, ...]
        columns, params = zip(*pairs, strict=True)
        placeholders = ", ".join("?" for _ in params)
        col_names = ", ".join(columns)
        query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
        self._execute(query, params)

    def _get_records(
        self,
        table: LiteralString,
        columns: tuple[LiteralString, ...] | None = None,
        condition: LiteralString | None = None,
        params: tuple[int | float | str | None, ...] = (),
    ) -> list[TSchema]:
        columns_str = ", ".join(columns) if columns else "*"
        query = (
            f"SELECT {columns_str} FROM {table} WHERE {condition}"
            if condition
            else f"SELECT {columns_str} FROM {table}"
        )
        return self._fetch(query, params)


class Element(NamedTuple):
    id: str
    name: str
    emoji: str


class ElementsDatabaseManager(DatabaseManager[Element]):
    def __init__(self, db_path):
        super().__init__(db_path)
        self._TABLE = "elements"

    def add_element(self, name: str, emoji: str):
        self._insert_record(self._TABLE, ("id", name), ("name", name), ("emoji", emoji))

    def get_element(self, id: str):
        records = self._get_records(self._TABLE, condition="id = ?", params=(id,))
        return Element(*records[0]) if records else None

    def bulk_add_elements(self, elements: list[tuple[str, str]]):
        records = [(element_id, element_id, emoji) for element_id, emoji in elements]
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.executemany(f"INSERT INTO {self._TABLE} (id, name, emoji) VALUES (?, ?, ?)", records)
            conn.commit()

    def get_all_elements(self, offset: int = 0, limit: int = 100):
        query = f"SELECT id, name, emoji FROM {self._TABLE} LIMIT ? OFFSET ?"
        records = self._fetch(query, (limit, offset))
        return [Element(*record) for record in records]


class Recipe(NamedTuple):
    id: str
    a: str
    b: str
    result: str


class RecipesDatabaseManager(DatabaseManager[Recipe]):
    def __init__(self, db_path):
        super().__init__(db_path)
        self._TABLE = "recipes"

    def add_recipes(self, a: str, b: str, result: str):
        if a > b:
            a, b = b, a
        id = f"{a}={b}"
        self._insert_record(self._TABLE, ("id", id), ("a", a), ("b", b), ("result", result))

    def get_recipes(self, name: str):
        records = self._get_records(self._TABLE, condition="name = ?", params=(name,))
        return [Recipe(*record) for record in records] if records else None

    def bulk_add_recipes(self, recipes: list[tuple[str, str, str]]):
        records: list[Recipe] = []
        for a, b, result in recipes:
            if a > b:
                a, b = b, a
            id = f"{a}={b}"
            records.append(Recipe(id, a, b, result))

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                f"INSERT INTO {self._TABLE} (id, a, b, result) VALUES (?, ?, ?, ?)", records
            )
            conn.commit()
