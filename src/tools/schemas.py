from __future__ import annotations

from pydantic import BaseModel, Field

from database.schemas import QueryResult


class SqlToolErrorResult(BaseModel):
    error: str
    details: str


class SqlTableListToolResult(BaseModel):
    tables: list[str] = Field(default_factory=list)


class SqlTableSchemaToolItem(BaseModel):
    table_name: str
    schema_sql: str


class SqlTableSchemaToolResult(BaseModel):
    schemas: list[SqlTableSchemaToolItem] = Field(default_factory=list)


class SqlQueryToolResult(BaseModel):
    columns: list[str] = Field(default_factory=list)
    rows: list[list[object]] = Field(default_factory=list)
    row_count: int
    stored_in_filesystem: bool = False
    filesystem_path: str | None = None
    filesystem_search_guidance: str | None = None

    @classmethod
    def from_query_result(cls, query_result: QueryResult) -> "SqlQueryToolResult":
        return cls(
            columns=query_result.columns,
            rows=query_result.rows,
            row_count=query_result.row_count,
        )
