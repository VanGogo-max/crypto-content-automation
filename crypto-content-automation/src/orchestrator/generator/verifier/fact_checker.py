# Copyright 2026 Георги Владимиров
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

from typing import List, Tuple, Dict
import re


class FactSource:
    def __init__(self, title: str, url: str, reliability_score: float):
        self.title = title
        self.url = url
        self.reliability_score = reliability_score


class FactCheckResult:
    def __init__(self, verified_text: str, sources: List[FactSource], score: float):
        self.verified_text = verified_text
        self.sources = sources
        self.score = score


class FactChecker:
    """
    Performs automatic factual validation by:
    - Extracting factual claims
    - Querying trusted sources
    - Scoring reliability
    """

    def __init__(self, web_client, trusted_domains: List[str]):
        self.web_client = web_client
        self.trusted_domains = trusted_domains

    def verify(self, text: str) -> Tuple[str, List[Dict]]:
        claims = self._extract_claims(text)
        sources = []

        for claim in claims:
            result = self.web_client.search(claim)
            best_source = self._select_best_source(result)
            if best_source:
                sources.append(best_source)

        verified_text = self._annotate(text, sources)
        return verified_text, [s.__dict__ for s in sources]

    def _extract_claims(self, text: str) -> List[str]:
        # Very simple NLP heuristic (to be replaced by NER later)
        sentences = re.split(r'\.\s+', text)
        factual = [s for s in sentences if any(char.isdigit() for char in s)]
        return factual

    def _select_best_source(self, search_results: List[FactSource]) -> FactSource | None:
        if not search_results:
            return None
        # Choose highest reliability score
        return max(search_results, key=lambda s: s.reliability_score)

    def _annotate(self, text: str, sources: List[FactSource]) -> str:
        if not sources:
            return text

        appendix = "\n\nSources:\n"
        for s in sources:
            appendix += f"- {s.title} ({s.url})\n"

        return text + appendix


# -------- Example Web Client Interface --------

class BaseWebClient:
    def search(self, query: str) -> List[FactSource]:
        raise NotImplementedError
