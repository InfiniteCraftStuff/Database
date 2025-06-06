import sqlite3
from typing import NamedTuple, LiteralString, Generic, TypeVar
from collections.abc import Iterable


Params = tuple[int | float | str | None, ...]

TSchema = TypeVar("TSchema", bound=NamedTuple)


class DatabaseManager(Generic[TSchema]):
    def __init__(self, db_path: str, table: LiteralString):
        self.db_path = db_path
        self._TABLE = table

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _execute(self, query: LiteralString, params: Params):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def _executemany(self, query: LiteralString, seq_of_params: Iterable[Params]):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, seq_of_params)
            conn.commit()

    def _fetch(self, query: LiteralString, params: Params):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def _insert_record(self, *pairs: tuple[LiteralString, int | float | str | None]):
        columns: tuple[LiteralString, ...]
        params: Params
        columns, params = zip(*pairs, strict=True)
        placeholders = ", ".join("?" for _ in params)
        col_names = ", ".join(columns)
        query = f"INSERT INTO {self._TABLE} ({col_names}) VALUES ({placeholders})"
        self._execute(query, params)

    def _insert_records(self, columns: tuple[LiteralString, ...], records: Iterable[TSchema]):
        columns_str = ", ".join(columns)
        placeholders = ", ".join("?" for _ in columns)
        query = f"INSERT OR IGNORE INTO {self._TABLE} ({columns_str}) VALUES ({placeholders})"
        self._executemany(query, records)

    def _get_records(
        self,
        columns: tuple[LiteralString, ...] | None = None,
        condition: LiteralString | None = None,
        params: Params = (),
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[TSchema]:
        columns_str = ", ".join(columns) if columns else "*"
        query = f"SELECT {columns_str} FROM {self._TABLE}"
        if condition:
            query += f" WHERE {condition}"
        if limit is not None:
            query += " LIMIT ?"
            params += (limit,)
        if offset is not None:
            query += " OFFSET ?"
            params += (offset,)

        return self._fetch(query, params)


class Element(NamedTuple):
    id: str
    name: str
    emoji: str


class ElementsDatabaseManager(DatabaseManager[Element]):
    def __init__(self, db_path: str):
        super().__init__(db_path, "elements")

    def add_element(self, name: str, emoji: str):
        self._insert_record(("id", name), ("name", name), ("emoji", emoji))

    def get_element(self, id: str):
        records = self._get_records(condition="id = ?", params=(id,))
        return Element(*records[0]) if records else None

    def bulk_add_elements(self, elements: list[tuple[str, str]]):
        records = [Element(element_id, element_id, emoji) for element_id, emoji in elements]
        self._insert_records(("id", "name", "emoji"), records)

    def get_all_elements(self, offset: int = 0, limit: int = 100):
        records = self._get_records(limit=limit, offset=offset)
        return [Element(*record) for record in records]


class Recipe(NamedTuple):
    id: str
    a: str
    b: str
    result: str


class RecipesDatabaseManager(DatabaseManager[Recipe]):
    def __init__(self, db_path: str):
        super().__init__(db_path, "recipes")

    def add_recipes(self, a: str, b: str, result: str):
        if a > b:
            a, b = b, a
        id = f"{a}={b}"
        self._insert_record(("id", id), ("a", a), ("b", b), ("result", result))

    def get_recipes(self, result: str):
        records = self._get_records(condition="result = ?", params=(result,))
        return [Recipe(*record) for record in records] if records else None

    def bulk_add_recipes(self, recipes: list[tuple[str, str, str]]):
        records: list[Recipe] = []
        for a, b, result in recipes:
            if a > b:
                a, b = b, a
            id = f"{a}={b}"
            records.append(Recipe(id, a, b, result))

        self._insert_records(("id", "a", "b", "result"), records)
