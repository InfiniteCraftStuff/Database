from typing import LiteralString, Literal
from collections.abc import Iterable

import sqlite3
import os


SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SRC_DIR)

DB_PATH = os.path.join(BASE_DIR, "storage", "elements.db")


type _FieldName = LiteralString
type _FieldDataType = Literal["TEXT"]
type _FieldConstraint = Literal["PRIMARY KEY", "NOT NULL"]
type _IterableFieldConstraints = tuple[_FieldConstraint, ...]
type _FieldConstraints = _IterableFieldConstraints | _FieldConstraint
type _OptionalFieldConstraints = _FieldConstraints | None
type _Field = tuple[_FieldName, _FieldDataType, _OptionalFieldConstraints]
type _Fields = Iterable[_Field]
type _TableName = LiteralString
type _FormattedField = LiteralString


def format_field(
    name: _FieldName, data: _FieldDataType, constraints: _OptionalFieldConstraints
) -> _FormattedField:
    parts: list[LiteralString] = [f'"{name}"', data]
    if constraints:
        if isinstance(constraints, str):
            parts.append(constraints)
        else:
            parts.extend(constraints)
    return " ".join(parts)


def create_table(conn: sqlite3.Connection, table_name: _TableName, fields: _Fields):
    cursor = conn.cursor()

    fields_str = ", ".join(
        format_field(name, data, constraints) for name, data, constraints in fields
    )

    query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({fields_str})'

    cursor.execute(query)

    conn.commit()


def main():
    with sqlite3.connect(DB_PATH) as conn:
        create_table(
            conn,
            "elements",
            (
                ("id", "TEXT", "PRIMARY KEY"),
                ("name", "TEXT", "NOT NULL"),
                ("emoji", "TEXT", None),
            ),  #
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
