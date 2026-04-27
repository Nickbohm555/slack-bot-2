from __future__ import annotations

import sqlite3
from pathlib import Path

from database.schemas import QueryResult, TableDefinitionResult, VisibleTablesResult

VISIBLE_VIRTUAL_TABLES = {"artifacts_fts"}

def list_visible_tables(db_path: Path) -> VisibleTablesResult:
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("PRAGMA table_list").fetchall()

    visible_tables: list[str] = []
    for schema_name, table_name, table_type, *_ in rows:
        if schema_name != "main":
            continue
        if table_name.startswith("sqlite_"):
            continue
        if table_type in {"shadow", "virtual"} and table_name not in VISIBLE_VIRTUAL_TABLES:
            continue
        visible_tables.append(table_name)

    tables = sorted(visible_tables)
    return VisibleTablesResult(
        tables=tables,
    )


def get_create_table_sql(db_path: Path, table_name: str) -> TableDefinitionResult:
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table' AND name = ?
            """,
            (table_name,),
        ).fetchone()

    sql = None
    if row is not None and row[0] is not None:
        sql = str(row[0])

    return TableDefinitionResult(
        table_name=table_name,
        sql=sql,
    )


def execute_query(
    db_path: Path,
    query: str,
) -> QueryResult:
    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description or ()]

    serialized_rows: list[list[object]] = []
    for row in rows:
        serialized_rows.append(list(row))

    row_count = len(serialized_rows)
    return QueryResult(
        columns=columns,
        rows=serialized_rows,
        row_count=row_count,
    )
