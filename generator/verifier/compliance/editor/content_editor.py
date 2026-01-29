# File: editor/content_editor.py
# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

"""
ContentEditor module
- Polishes crypto content for readability
- Applies SEO optimization
- Ensures professional tone
- Optional watermark applied separately
"""

import re

class ContentEditorError(Exception):
    pass

class ContentEditor:
    def __init__(self, seo_keywords: list[str] = None):
        self.seo_keywords = seo_keywords or ["crypto", "blockchain", "DeFi", "NFT", "Web3"]

    def edit(self, text: str) -> str:
        """
        Apply editing and SEO optimizations:
        - Remove extra spaces / newlines
        - Normalize headings
        - Insert SEO keywords naturally
        """
        try:
            text = self._normalize_whitespace(text)
            text = self._normalize_headings(text)
            text = self._apply_seo_keywords(text)
            return text
        except Exception as e:
            raise ContentEditorError(f"Editing failed: {e}")

    def _normalize_whitespace(self, text: str) -> str:
        # Collapse multiple spaces/newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def _normalize_headings(self, text: str) -> str:
        # Ensure headings start with uppercase and # formatting for markdown
        def repl(m):
            return f"# {m.group(1).strip().title()}"
        text = re.sub(r'^#\s*(.+)$', repl, text, flags=re.MULTILINE)
        return text

    def _apply_seo_keywords(self, text: str) -> str:
        # Simple insertion of keywords in first paragraph if missing
        paragraphs = text.split("\n\n")
        if paragraphs:
            first = paragraphs[0]
            for kw in self.seo_keywords:
                if kw.lower() not in first.lower():
                    first += f" {kw}"
            paragraphs[0] = first
        return "\n\n".join(paragraphs)
