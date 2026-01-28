# Copyright 2026 Георги Владимиров
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

from typing import Dict, Any
import uuid
import datetime


class AIGenerator:
    """
    Responsible for generating initial educational crypto content
    using an LLM backend and strict prompt templates.
    """

    def __init__(self, llm_client, prompt_templates: Dict[str, str]):
        self.llm = llm_client
        self.prompts = prompt_templates

    def generate(self, topic: str) -> str:
        prompt = self._build_prompt(topic)
        response = self.llm.complete(prompt)
        return self._post_process(response)

    def _build_prompt(self, topic: str) -> str:
        base_prompt = self.prompts.get("educational_article")
        if not base_prompt:
            raise ValueError("Missing 'educational_article' prompt template")

        return base_prompt.format(
            topic=topic,
            date=datetime.datetime.utcnow().isoformat()
        )

    def _post_process(self, text: str) -> str:
        # Basic sanitation and normalization
        cleaned = text.strip()
        cleaned = cleaned.replace("\r\n", "\n")
        return cleaned


# -------- Example LLM Client Interface --------

class BaseLLMClient:
    def complete(self, prompt: str) -> str:
        raise NotImplementedError


# -------- Prompt Registry Loader --------

def load_default_prompts() -> Dict[str, str]:
    return {
        "educational_article": (
            "You are a professional financial and blockchain analyst.\n"
            "Write a detailed, factual, neutral educational article about:\n"
            "Topic: {topic}\n\n"
            "Rules:\n"
            "- No financial advice\n"
            "- No price predictions\n"
            "- Cite verifiable sources\n"
            "- Avoid hype and marketing language\n"
            "- Use formal analytical style\n\n"
            "Date: {date}\n"
            "Article:\n"
        )
    }
