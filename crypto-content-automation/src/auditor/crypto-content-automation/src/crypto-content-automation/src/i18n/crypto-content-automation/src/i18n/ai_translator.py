# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0

from i18n.language_router import BaseTranslator


class AITranslator(BaseTranslator):
    def __init__(self, llm_client):
        self.llm = llm_client

    def translate(self, text: str, target_lang: str) -> str:
        prompt = f"Translate the following text to {target_lang} preserving financial terminology:\n\n{text}"
        return self.llm.generate(prompt)
