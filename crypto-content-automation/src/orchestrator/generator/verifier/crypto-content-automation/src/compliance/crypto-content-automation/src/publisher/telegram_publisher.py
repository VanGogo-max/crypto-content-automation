# Copyright 2026 Георги Владимиров
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

import requests
import time
from typing import Dict, Any


class TelegramPublishError(Exception):
    pass


class TelegramPublisher:
    """
    Publishes verified and compliant content to a Telegram channel
    using the official Telegram Bot API.
    """

    TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, bot_token: str, channel_id: str, parse_mode: str = "HTML"):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.parse_mode = parse_mode

    def publish(self, text: str, metadata: Dict[str, Any]):
        payload = {
            "chat_id": self.channel_id,
            "text": self._format(text, metadata),
            "parse_mode": self.parse_mode,
            "disable_web_page_preview": False
        }

        url = self.TELEGRAM_API_URL.format(
            token=self.bot_token,
            method="sendMessage"
        )

        response = requests.post(url, json=payload, timeout=15)

        if response.status_code != 200:
            raise TelegramPublishError(
                f"Telegram API error: {response.status_code} - {response.text}"
            )

        data = response.json()
        if not data.get("ok"):
            raise TelegramPublishError(f"Telegram rejected message: {data}")

        return data

    def _format(self, text: str, metadata: Dict[str, Any]) -> str:
        """
        Formats article for Telegram with source attribution and disclaimer.
        """
        sources = metadata.get("sources", [])

        footer = "\n\n—\n"
        footer += "<b>Sources:</b>\n"
        for s in sources:
            footer += f"• <a href=\"{s['url']}\">{s['title']}</a>\n"

        footer += "\n<i>Educational content. Not financial advice.</i>"

        return text + footer


# -------- Rate Limited Wrapper --------

class RateLimitedTelegramPublisher(TelegramPublisher):
    def __init__(self, bot_token: str, channel_id: str, max_per_minute: int = 20):
        super().__init__(bot_token, channel_id)
        self.delay = 60.0 / max_per_minute
        self._last_sent = 0.0

    def publish(self, text: str, metadata: Dict[str, Any]):
        now = time.time()
        elapsed = now - self._last_sent

        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        result = super().publish(text, metadata)
        self._last_sent = time.time()
        return result
