from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

from agents.filesystem import build_notes_backend
from agents.logging import log_graph_messages, normalize_messages
from agents.middleware import SlackToolProgressMiddleware
from agents.prompt import SINGLE_AGENT_SYSTEM_PROMPT
from agents.schemas import RuntimeAnswer, UnavailableChatModel
from config import Settings, get_settings
from tools.database import build_sql_tools


logger = logging.getLogger("agents.builder")


def build_agent_model(settings: Settings | None = None) -> BaseChatModel:
    runtime_settings = settings or get_settings()
    try:
        return init_chat_model(
            runtime_settings.single_agent.model,
            model_provider=runtime_settings.single_agent.provider,
        )
    except ImportError as exc:
        return UnavailableChatModel(
            provider=runtime_settings.single_agent.provider,
            model_name=runtime_settings.single_agent.model,
            import_error=str(exc),
        )


def _extract_final_assistant_answer(messages: list[dict[str, object]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "assistant":
            return str(message.get("content", ""))
    return ""


def normalize_agent_result(result: dict[str, object]) -> RuntimeAnswer:
    messages = normalize_messages(list(result.get("messages", [])))
    return RuntimeAnswer(
        answer=str(result.get("answer") or _extract_final_assistant_answer(messages)),
        runtime_mode=str(result.get("runtime_mode") or "single_agent"),
        messages=messages,
    )


def invoke_agent_runtime(
    *,
    text: str,
    thread_id: str,
    slack_user_id: str,
    conversation_key: str,
    sqlite_db_path: Path,
    checkpointer: object | None = None,
    settings: Settings | None = None,
    from_slack_ui: bool = False,
    update_placeholder: Callable[[str], None] | None = None,
) -> RuntimeAnswer:
    runtime_settings = settings or get_settings()

    agent_model = build_agent_model(runtime_settings)
    agent_tools = build_sql_tools(
        sqlite_db_path,
        query_max_cell_chars=800,
    )
    agent_backend = build_notes_backend(settings=runtime_settings)
    agent_input = {
        "messages": [{"role": "user", "content": text}],
        "files": {},
    }
    agent_invoke_config = {"configurable": {"thread_id": thread_id}}
    middleware = []
    if from_slack_ui and update_placeholder is not None:
        middleware.append(
            SlackToolProgressMiddleware(update_placeholder=update_placeholder)
        )

    logger.info(
        "agent_runtime conversation_start thread_id=%s slack_user_id=%s conversation_key=%s input=%s from_slack_ui=%s",
        thread_id,
        slack_user_id,
        conversation_key,
        text,
        from_slack_ui,
    )
    try:
        coordinator_agent = create_deep_agent(
            model=agent_model,
            tools=agent_tools,
            system_prompt=SINGLE_AGENT_SYSTEM_PROMPT,
            backend=agent_backend,
            skills=[],
            checkpointer=checkpointer,
            middleware=middleware,
            name="coordinator_agent",
        )
        result = coordinator_agent.invoke(agent_input, agent_invoke_config)
        log_graph_messages(list(result.get("messages", [])), thread_id=thread_id)
        return normalize_agent_result(result)
    except Exception:
        logger.exception(
            "agent_runtime conversation_failed thread_id=%s slack_user_id=%s conversation_key=%s",
            thread_id,
            slack_user_id,
            conversation_key,
        )
        return RuntimeAnswer(answer="", error="conversation_runtime_failed")
