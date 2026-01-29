# File: legal/hash_notary.py
# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

"""
Deterministic SHA256 notary with canonical serialization.

Guarantees:
- Stable hashing (no whitespace / encoding drift)
- UTF-8 normalization (NFKC)
- Optional structured payload support (dict -> canonical JSON)
- Timestamp binding handled by Ethereum client
"""

import hashlib
import json
import unicodedata
from typing import Any, Dict


class HashNotaryError(Exception):
    pass


class HashNotary:
    def __init__(self, normalize_unicode: bool = True):
        self.normalize_unicode = normalize_unicode

    def _normalize_text(self, text: str) -> str:
        if self.normalize_unicode:
            return unicodedata.normalize("NFKC", text)
        return text

    def _canonical_json(self, data: Dict[str, Any]) -> str:
        """
        Deterministic JSON serialization:
        - Sorted keys
        - No whitespace
        - UTF-8
        """
        try:
            return json.dumps(
                data,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":")
            )
        except Exception as e:
            raise HashNotaryError(f"Canonical JSON serialization failed: {e}")

    def hash_text(self, text: str) -> str:
        """
        Hash raw text deterministically (UTF-8, normalized).
        """
        try:
            normalized = self._normalize_text(text)
            return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        except Exception as e:
            raise HashNotaryError(f"Text hashing failed: {e}")

    def hash_structured(self, payload: Dict[str, Any]) -> str:
        """
        Hash structured data (e.g. metadata, sources, legal fields)
        via canonical JSON.
        """
        canonical = self._canonical_json(payload)
        return self.hash_text(canonical)

    def hash_with_watermark(self, text: str, watermark: str) -> str:
        """
        Hash combined content + legal watermark deterministically.
        """
        combined = f"{text}\n---\n{watermark}"
        return self.hash_text(combined)

    def verify(self, text: str, expected_sha256: str) -> bool:
        """
        Deterministic verification.
        """
        computed = self.hash_text(text)
        return computed.lower() == expected_sha256.lower()
