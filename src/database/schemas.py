from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class VisibleTablesResult(BaseModel):
    tables: list[str] = Field(default_factory=list)


class TableDefinitionResult(BaseModel):
    table_name: str
    sql: str | None = None


class QueryResult(BaseModel):
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    row_count: int
