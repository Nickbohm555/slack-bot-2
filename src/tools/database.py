from __future__ import annotations

import json
import uuid
from pathlib import Path

from deepagents.backends import StateBackend
from langchain.tools import tool
from pydantic_core import to_jsonable_python

from config import get_settings
from database.sqlite import execute_query, get_create_table_sql, list_visible_tables
from tools.schemas import (
    SqlQueryToolResult,
    SqlTableListToolResult,
    SqlTableSchemaToolItem,
    SqlTableSchemaToolResult,
    SqlToolErrorResult,
)


def _default_db_path() -> Path:
    return Path(get_settings().sqlite.db_path)


def _resolve_db_path(*, db_path: Path | None = None) -> Path:
    return db_path or _default_db_path()


def _result_needs_filesystem_dump(
    columns: list[str],
    rows: list[list[object]],
    *,
    max_cell_chars: int,
    max_inline_chars: int,
) -> bool:
    for row in rows:
        for value in row:
            if isinstance(value, str) and len(value) > max_cell_chars:
                return True
    serialized_rows = [
        {
            column: to_jsonable_python(value)
            for column, value in zip(columns, row, strict=False)
        }
        for row in rows
    ]
    return len(json.dumps(serialized_rows, ensure_ascii=True, default=str)) > max_inline_chars


def _format_markdown_value(value: object) -> str:
    if value is None:
        return "`null`"
    if isinstance(value, (int, float, bool)):
        return f"`{value}`"
    text_value = str(value)
    if "\n" not in text_value:
        return text_value
    return f"\n```text\n{text_value}\n```"


def _dump_large_query_result_to_state(
    *,
    query: str,
    columns: list[str],
    rows: list[list[object]],
    max_preview_rows: int,
) -> tuple[str, list[list[object]]]:
    file_path = f"/sql_large/{uuid.uuid4().hex[:12]}.md"
    state_backend = StateBackend()

    markdown_lines = [
        "# SQL Large Result",
        "",
        "## Query",
        "```sql",
        query,
        "```",
        "",
        f"- Row count: {len(rows)}",
        f"- Columns: {', '.join(columns)}",
        "",
    ]
    for row_index, row in enumerate(rows, start=1):
        markdown_lines.append(f"## Row {row_index}")
        for column, value in zip(columns, row, strict=False):
            formatted_value = _format_markdown_value(value)
            if formatted_value.startswith("\n```text"):
                markdown_lines.append(f"- {column}:{formatted_value}")
            else:
                markdown_lines.append(f"- {column}: {formatted_value}")
        markdown_lines.append("")

    write_result = state_backend.write(file_path, "\n".join(markdown_lines).rstrip() + "\n")
    if write_result.error is not None:
        raise RuntimeError(write_result.error)

    return file_path, rows[:max_preview_rows]


def list_sqlite_tables(*, db_path: Path | None = None) -> SqlTableListToolResult:
    resolved_db_path = _resolve_db_path(db_path=db_path)
    visible_tables_result = list_visible_tables(resolved_db_path)
    tables = visible_tables_result.tables
    return SqlTableListToolResult(
        tables=tables,
    )


list_tables = list_sqlite_tables


def inspect_table_schema(
    table_names: str,
    *,
    db_path: Path | None = None,
) -> SqlTableSchemaToolResult | SqlToolErrorResult:
    resolved_db_path = _resolve_db_path(db_path=db_path)
    visible_tables_result = list_visible_tables(resolved_db_path)
    available_tables = set(visible_tables_result.tables)
    requested_tables = [name.strip() for name in table_names.split(",") if name.strip()]
    if not requested_tables:
        error = "No tables provided."
        details = "Pass one or more comma-separated table names from sql_db_list_tables."
        return SqlToolErrorResult(
            error=error,
            details=details,
        )

    unknown_tables = [table_name for table_name in requested_tables if table_name not in available_tables]
    if unknown_tables:
        unknown_table_names = ", ".join(unknown_tables)
        error = f"Unknown tables: {unknown_table_names}"
        details = "Call sql_db_list_tables first and request only known table names."
        return SqlToolErrorResult(
            error=error,
            details=details,
        )

    schemas: list[SqlTableSchemaToolItem] = []
    for table_name in requested_tables:
        table_definition = get_create_table_sql(resolved_db_path, table_name)
        create_sql = table_definition.sql or f"CREATE TABLE {table_name} (...)"
        schemas.append(
            SqlTableSchemaToolItem(
                table_name=table_name,
                schema_sql=create_sql,
            )
        )

    return SqlTableSchemaToolResult(
        schemas=schemas,
    )


inspect_columns = inspect_table_schema


def execute_sql_query(query: str, *, db_path: Path | None = None) -> SqlQueryToolResult | SqlToolErrorResult:
    """Execute a SQLite query and return structured rows."""
    try:
        query_result = execute_query(_resolve_db_path(db_path=db_path), query)
        return SqlQueryToolResult.from_query_result(query_result)
    except Exception as exc:
        error = str(exc)
        details = (
            "execution_failed: before retrying, make sure table names and column "
            "names are valid by using sql_db_list_tables and sql_db_schema."
        )
        query_error = SqlToolErrorResult(
            error=error,
            details=details,
        )
        return query_error


execute_sql = execute_sql_query


def build_sql_tools(
    db_path: Path,
    *,
    query_max_cell_chars: int,
    query_max_inline_chars: int = 5000,
) -> tuple[object, object, object]:
    resolved_db_path = db_path.resolve()

    @tool("sql_db_list_tables")
    def list_tables_tool(tool_input: str = "") -> dict[str, object]:
        """sql_db_list_tables: Input is an empty string. Output contains the table names in a tables field."""
        del tool_input
        table_list_result = list_sqlite_tables(db_path=resolved_db_path)
        return table_list_result.model_dump(mode="python")

    @tool("sql_db_schema")
    def inspect_columns_tool(table_names: str) -> dict[str, object]:
        """sql_db_schema: Input is a comma-separated list of tables. Output contains schemas with table_name and schema_sql fields. Call sql_db_list_tables first. Example Input: table1, table2, table3"""
        table_schema_result = inspect_table_schema(table_names, db_path=resolved_db_path)
        return table_schema_result.model_dump(mode="python")

    @tool("sql_db_query")
    def execute_sql_tool(query: str) -> dict[str, object]:
        """sql_db_query: Input is a SQL query using only tables and columns already confirmed by sql_db_list_tables or sql_db_schema. Output contains columns, rows, and row_count. If the result is large, it is written to `/sql_large/<random>.md` and the tool returns that file path plus search guidance instead of the full inline result. For FTS, use `FROM artifacts_fts JOIN artifacts a ON a.artifact_id = artifacts_fts.artifact_id WHERE artifacts_fts MATCH 'term1 AND term2'`."""
        try:
            query_result = execute_query(resolved_db_path, query)
            columns = query_result.columns
            rows = query_result.rows
            if _result_needs_filesystem_dump(
                columns,
                rows,
                max_cell_chars=query_max_cell_chars,
                max_inline_chars=query_max_inline_chars,
            ):
                filesystem_path, preview_rows = _dump_large_query_result_to_state(
                    query=query,
                    columns=columns,
                    rows=rows,
                    max_preview_rows=3,
                )
                sql_query_result = SqlQueryToolResult(
                    columns=columns,
                    rows=preview_rows,
                    row_count=len(rows),
                    stored_in_filesystem=True,
                    filesystem_path=filesystem_path,
                    filesystem_search_guidance=(
                        f"Use `grep` on `{filesystem_path}` for exact names, IDs, dates, titles, "
                        "or keywords from the user question. After grep finds candidate rows, use "
                        "targeted `read` on that file and avoid reading the entire document."
                    ),
                )
                return sql_query_result.model_dump(mode="python")

            sql_query_result = SqlQueryToolResult.from_query_result(query_result)
            return sql_query_result.model_dump(mode="python")
        except Exception as exc:
            error = str(exc)
            details = (
                "execution_failed: before retrying, verify table names and column "
                "names with sql_db_list_tables and sql_db_schema, then rewrite the query."
            )
            query_error = SqlToolErrorResult(
                error=error,
                details=details,
            )
            return query_error.model_dump(mode="python")

    return (list_tables_tool, inspect_columns_tool, execute_sql_tool)


list_tables_tool, inspect_columns_tool, execute_sql_tool = build_sql_tools(
    _default_db_path(),
    query_max_cell_chars=800,
)
