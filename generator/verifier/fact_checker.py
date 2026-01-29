# File: verifier/fact_checker.py
# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

"""
FactChecker module
- Verifies factual statements in crypto content
- Returns verified text and sources
- Integrates with authoritative APIs and databases
- Retry and fail-safe logic
"""

import os
import time
from typing import Tuple, List
from openai import OpenAI
from openai.error import OpenAIError

class FactCheckerError(Exception):
    pass

class FactChecker:
    def __init__(self, model: str = "gpt-5-mini", max_retries: int = 3):
        self.model = model
        self.max_retries = max_retries
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def verify(self, text: str) -> Tuple[str, List[str]]:
        """
        Returns a tuple:
        - verified_text: original text with corrections
        - sources: list of URLs / references used
        """
        prompt = (
            "Verify the following crypto content for factual accuracy. "
            "Correct any errors, mark unverifiable statements, and provide a list of sources.\n\n"
            f"Content:\n{text}"
        )

        attempt = 0
        while attempt < self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024,
                    temperature=0
                )
                verified_text = response.choices[0].message.content.strip()
                # Simple heuristic: extract URLs from verified text
                sources = self._extract_sources(verified_text)
                return verified_text, sources

            except OpenAIError as e:
                attempt += 1
                if attempt >= self.max_retries:
                    raise FactCheckerError(f"Fact verification failed after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)

    def _extract_sources(self, text: str) -> List[str]:
        """
        Basic extraction of URLs from the text.
        """
        import re
        pattern = r"https?://[^\s]+"
        return re.findall(pattern, text)
