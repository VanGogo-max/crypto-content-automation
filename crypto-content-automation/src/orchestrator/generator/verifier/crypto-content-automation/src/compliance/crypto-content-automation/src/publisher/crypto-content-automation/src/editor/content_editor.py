# Copyright 2026 Георги Владимиров
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

import re
from typing import List


class ContentEditor:
    """
    Cleans, structures and optimizes verified content for:
    - Blog (Blogger)
    - Telegram
    - SEO
    - Readability
    """

    def __init__(self, max_paragraph_length: int = 5):
        self.max_paragraph_length = max_paragraph_length

    def edit(self, text: str) -> str:
        text = self._normalize(text)
        paragraphs = self._split_paragraphs(text)
        paragraphs = self._shorten_paragraphs(paragraphs)
        paragraphs = self._add_headings(paragraphs)
        return "\n\n".join(paragraphs)

    def _normalize(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    def _split_paragraphs(self, text: str) -> List[str]:
        return [p.strip() for p in text.split("\n\n") if p.strip()]

    def _shorten_paragraphs(self, paragraphs: List[str]) -> List[str]:
        processed = []
        for p in paragraphs:
            sentences = re.split(r"(?<=[.!?])\s+", p)
            if len(sentences) <= self.max_paragraph_length:
                processed.append(p)
            else:
                chunk = []
                for i in range(0, len(sentences), self.max_paragraph_length):
                    chunk.append(" ".join(sentences[i:i+self.max_paragraph_length]))
                processed.extend(chunk)
        return processed

    def _add_headings(self, paragraphs: List[str]) -> List[str]:
        result = []
        for i, p in enumerate(paragraphs):
            if i == 0:
                result.append(f"<b>Introduction</b>\n{p}")
            elif i == len(paragraphs) - 1:
                result.append(f"<b>Conclusion</b>\n{p}")
            else:
                result.append(p)
        return result
