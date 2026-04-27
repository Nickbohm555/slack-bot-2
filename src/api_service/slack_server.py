import logging
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from api_service.schemas import SlackInboundMessage
from api_service.slack_progress import SlackMessagePlaceholder
from api_service.slack_service import build_inbound_message, handle_slack_message, should_ignore_message
from app_logging import configure_logging
from config import Settings, get_settings
from database import build_runtime_dependencies


PROJECT_ROOT = Path(__file__).resolve().parents[2]
logger = logging.getLogger("api_service.slack_server")


def _run_message_lifecycle(
    message: SlackInboundMessage,
    *,
    say,
    client,
    runtime_settings: Settings,
    dependencies,
    reply_thread_ts: str | None,
) -> None:
    placeholder = SlackMessagePlaceholder(
        client=client,
        channel_id=message.slack_channel_id,
        thread_ts=reply_thread_ts,
    )
    placeholder.start()
    response = handle_slack_message(
        message,
        settings=runtime_settings,
        dependencies=dependencies,
        from_slack_ui=True,
        update_placeholder=placeholder.update_for_stage,
    )
    placeholder.finish(response.text)


def build_app(settings: Settings | None = None) -> App:
    runtime_settings = settings or get_settings()
    app = App(token=runtime_settings.slack.bot_token)
    dependencies = build_runtime_dependencies(runtime_settings)

    @app.event("message")
    def handle_direct_messages(body: dict[str, object], say, client) -> None:
        event = body.get("event")
        if not isinstance(event, dict):
            return
        if event.get("channel_type") != "im" or should_ignore_message(event):
            return

        message = build_inbound_message(event, source="dm")
        show_placeholder = bool(message.text.strip()) and message.text.strip().lower() not in {"new", "/new"}

        if show_placeholder:
            _run_message_lifecycle(
                message,
                say=say,
                client=client,
                runtime_settings=runtime_settings,
                dependencies=dependencies,
                reply_thread_ts=None,
            )
            return

        response = handle_slack_message(
            message,
            settings=runtime_settings,
            dependencies=dependencies,
        )
        say(text=response.text)

    @app.event("app_mention")
    def handle_mentions(body: dict[str, object], say, client) -> None:
        event = body.get("event")
        if not isinstance(event, dict) or should_ignore_message(event):
            return

        message = build_inbound_message(event, source="channel")
        reply_thread_ts = message.slack_thread_ts or message.slack_message_ts
        show_placeholder = bool(message.text.strip()) and message.text.strip().lower() not in {"new", "/new"}

        if show_placeholder:
            _run_message_lifecycle(
                message,
                say=say,
                client=client,
                runtime_settings=runtime_settings,
                dependencies=dependencies,
                reply_thread_ts=reply_thread_ts,
            )
            return

        response = handle_slack_message(
            message,
            settings=runtime_settings,
            dependencies=dependencies,
        )
        if response.reply_thread_ts is None:
            say(text=response.text)
            return
        say(text=response.text, thread_ts=response.reply_thread_ts)

    return app


def run() -> None:
    configure_logging()
    load_dotenv(PROJECT_ROOT / ".env")
    settings = get_settings()
    app = build_app(settings)
    SocketModeHandler(app, settings.slack.app_token).start()
