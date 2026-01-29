# File: generator/ai_generator.py
# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0

import os
import time
from typing import Optional
from openai import OpenAI
from openai.error import OpenAIError

class AIGeneratorError(Exception):
    pass

class AIGenerator:
    def __init__(self, model: str = "gpt-5-mini", max_retries: int = 3):
        self.model = model
        self.max_retries = max_retries
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate(self, topic: str, max_tokens: int = 1024) -> str:
        """
        Generates professional-grade crypto educational content.
        Retries on failure.
        """
        prompt = f"Write a professional, factual, SEO-friendly crypto article on: {topic}"
        attempt = 0

        while attempt < self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                content = response.choices[0].message.content.strip()
                if not content:
                    raise AIGeneratorError("Empty content returned by LLM")
                return content

            except OpenAIError as e:
                attempt += 1
                if attempt >= self.max_retries:
                    raise AIGeneratorError(f"LLM generation failed after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # exponential backoff
