import sqlite3
from typing import NamedTuple, LiteralString, Generic, TypeVar
from collections.abc import Iterable

type Param = int | float | str | None
type Params = tuple[Param, ...]

TSchema = TypeVar("TSchema", bound=NamedTuple)


class DatabaseManager(Generic[TSchema]):
    def __init__(self, db_path: str, table: LiteralString):
        self.db_path: str = db_path
        self._TABLE: LiteralString = table

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _execute(self, query: LiteralString, params: Params = ()):
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

    def _insert_record(self, values: dict[LiteralString, Param]):
        columns = tuple(values.keys())
        params = tuple(values.values())
        placeholders = ", ".join("?" for _ in columns)
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
        condition: LiteralString | None = None,
        params: Params = (),
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[TSchema]:
        query = f"SELECT * FROM {self._TABLE}"
        if condition:
            query += f" WHERE {condition}"
        if limit is not None:
            query += " LIMIT ?"
            params += (limit,)
        if offset is not None:
            query += " OFFSET ?"
            params += (offset,)

        return self._fetch(query, params)

    def _get_record(self, condition: LiteralString, params: Params = ()) -> TSchema | None:
        query = f"SELECT * FROM {self._TABLE}"
        if condition:
            query += f" WHERE {condition}"

        records = tuple(self._fetch(query, params))
        if len(records) > 1:
            raise Exception("More than one record!")
        if not records:
            return None
        return records[0]

    def _update_record(
        self, updates: dict[LiteralString, Param], condition: LiteralString, params: Params = ()
    ):
        columns_str = ", ".join(f"{col}=?" for col in updates)
        update_values = tuple(updates.values())
        query = f"UPDATE {self._TABLE} SET {columns_str} WHERE {condition}"
        self._execute(query, update_values + params)
