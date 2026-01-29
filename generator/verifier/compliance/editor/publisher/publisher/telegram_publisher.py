# File: publisher/telegram_publisher.py
# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

"""
TelegramPublisher module
- Publishes content to Telegram channels or groups via Bot API
- Returns message ID for audit
"""

import os
from typing import Dict
import requests

class TelegramPublisherError(Exception):
    pass

class TelegramPublisher:
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        if not self.bot_token or not self.chat_id:
            raise TelegramPublisherError("Missing bot token or chat ID")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def publish(self, text: str, metadata: Dict = None, language: str = "en") -> int:
        """
        Sends a message to Telegram.
        Returns the message ID.
        """
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            resp = requests.post(self.api_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                raise TelegramPublisherError(f"Telegram API error: {data}")
            return data["result"]["message_id"]
        except Exception as e:
            raise TelegramPublisherError(f"Failed to publish to Telegram: {e}")
