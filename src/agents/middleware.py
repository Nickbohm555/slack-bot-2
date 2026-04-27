from __future__ import annotations

from collections.abc import Callable

from langchain.agents.middleware.types import AgentMiddleware, ToolCallRequest


SQL_TOOL_NAMES = {
    "sql_db_list_tables",
    "sql_db_schema",
    "sql_db_query",
}

FILESYSTEM_TOOL_NAMES = {
    "ls",
    "read",
    "read_file",
    "glob",
    "grep",
}


class SlackToolProgressMiddleware(AgentMiddleware):
    def __init__(self, update_placeholder: Callable[[str], None]) -> None:
        self.update_placeholder = update_placeholder

    def wrap_tool_call(self, request: ToolCallRequest, handler):
        tool_name = str((request.tool_call or {}).get("name") or "")

        if tool_name in FILESYSTEM_TOOL_NAMES:
            self.update_placeholder("filesystem")
        elif tool_name in SQL_TOOL_NAMES:
            self.update_placeholder("sql")

        return handler(request)
