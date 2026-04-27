from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Any


logger = logging.getLogger("api_service.slack_progress")

FILESYSTEM_STAGE_MESSAGES = (
    "Looking through my notes...",
    "Scanning my notes...",
)

SQL_STAGE_MESSAGES = (
    "Searching the database...",
    "Pulling the answer from the database...",
)


@dataclass
class SlackMessagePlaceholder:
    client: Any
    channel_id: str
    thread_ts: str | None = None
    message_ts: str | None = None
    current_text: str | None = None

    def start(self) -> None:
        self._set_text("thinking...")

    def update_for_stage(self, stage: str) -> None:
        if stage == "filesystem":
            self._set_text(random.choice(FILESYSTEM_STAGE_MESSAGES))
        elif stage == "sql":
            self._set_text(random.choice(SQL_STAGE_MESSAGES))

    def finish(self, text: str) -> None:
        self._set_text(text, force=True)

    def _set_text(self, text: str, *, force: bool = False) -> None:
        if not force and text == self.current_text:
            return
        try:
            if self.message_ts is None:
                payload: dict[str, object] = {
                    "channel": self.channel_id,
                    "text": text,
                }
                if self.thread_ts is not None:
                    payload["thread_ts"] = self.thread_ts
                response = self.client.chat_postMessage(**payload)
                self.message_ts = str(response["ts"])
            else:
                self.client.chat_update(
                    channel=self.channel_id,
                    ts=self.message_ts,
                    text=text,
                )
            self.current_text = text
        except Exception:
            logger.exception(
                "slack_placeholder_update_failed channel=%s thread_ts=%s",
                self.channel_id,
                self.thread_ts,
            )
