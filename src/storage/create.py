from typing import LiteralString
from collections.abc import Iterable

import sqlite3
import os


SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SRC_DIR)

DB_PATH = os.path.join(BASE_DIR, "storage", "elements.db")


_FieldName = LiteralString
_FieldDataType = LiteralString
_FieldConstraint = LiteralString
_FieldConstraints = Iterable[_FieldConstraint] | _FieldConstraint
_Field = tuple[_FieldName, _FieldDataType, _FieldConstraints | None]


def format_field(name: _FieldName, data: _FieldDataType, constraints: _FieldConstraints | None):
    parts: list[LiteralString] = [f'"{name}"', data]
    if constraints:
        if isinstance(constraints, str):
            parts.append(constraints)
        else:
            parts.extend(constraints)
    return " ".join(parts)


def create_table(conn: sqlite3.Connection, table_name: LiteralString, fields: Iterable[_Field]):
    cursor = conn.cursor()

    fields_str = ", ".join(format_field(name, data, constraints) for name, data, constraints in fields)

    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({fields_str})')

    conn.commit()


def main():
    with sqlite3.connect(DB_PATH) as conn:
        create_table(
            conn,
            "elements",
            (("id", "TEXT", "PRIMARY KEY"), ("name", "TEXT", "NOT NULL"), ("emoji", "TEXT", None)),
        )

        create_table(
            conn,
            "recipes",
            (
                ("id", "TEXT", "PRIMARY KEY"),
                ("a", "TEXT", "NOT NULL"),
                ("b", "TEXT", "NOT NULL"),
                ("result", "TEXT", "NOT NULL"),
            ),
        )


if __name__ == "__main__":
    main()
