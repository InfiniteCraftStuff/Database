import sqlite3
from _typeshed import StrOrBytesPath
from typing import Iterable, LiteralString, Generic, TypeVar

T = TypeVar("T")


class DatabaseManager(Generic[T]):
    def __init__(self, db_path: StrOrBytesPath):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _execute(self, query: LiteralString, params: Iterable[int | float | str | None] = ()):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            conn.commit()

    def _fetch(self, query: LiteralString, params: Iterable[int | float | str | None] = ()):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
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
        params: Iterable[int | float | str | None] = (),
    ) -> list[T]:
        columns_str = ", ".join(columns) if columns else "*"
        query = (
            f"SELECT {columns_str} FROM {table} WHERE {condition}"
            if condition
            else f"SELECT {columns_str} FROM {table}"
        )
        return self._fetch(query, params)


class ElementsDatabaseManager(DatabaseManager[tuple[str, str, str]]):
    def __init__(self, db_path):
        super().__init__(db_path)
        self._TABLE = "recipes"

    def add_element(self, name: str, emoji: str):
        self._insert_record(self._TABLE, ("id", name), ("name", name), ("emoji", emoji))

    def get_element(self, id: str):
        records = self._get_records(self._TABLE, condition="id = ?", params=(id,))
        return records[0] if records else None


class RecipesDatabaseManager(DatabaseManager[tuple[str, str, str, str]]):
    def __init__(self, db_path):
        super().__init__(db_path)
        self._TABLE = "recipes"

    def add_recipes(self, a: str, b: str, result: str):
        self._insert_record(self._TABLE, ("id", result), ("a", a), ("b", b), ("result", result))

    def get_recipe(self, id: str):
        records = self._get_records(self._TABLE, condition="id = ?", params=(id,))
        return records[0] if records else None
