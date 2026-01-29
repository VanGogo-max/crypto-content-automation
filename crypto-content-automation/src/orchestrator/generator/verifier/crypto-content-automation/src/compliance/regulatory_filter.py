# Copyright 2026 Георги Владимиров
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

import re
from typing import List, Dict


class ComplianceViolation(Exception):
    pass


class RegulatoryFilter:
    """
    Blocks content that may violate financial, advertising, or consumer protection rules.
    Detects:
    - Financial advice
    - Profit guarantees
    - Price predictions
    - Promotional / scam language
    - Call-to-action for investing
    """

    def __init__(self):
        self.forbidden_patterns = self._load_forbidden_patterns()

    def validate(self, text: str) -> bool:
        violations = self._scan(text)
        if violations:
            raise ComplianceViolation(f"Compliance violations detected: {violations}")
        return True

    def _scan(self, text: str) -> List[Dict]:
        found = []
        for rule_name, patterns in self.forbidden_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found.append({
                        "rule": rule_name,
                        "pattern": pattern
                    })
        return found

    def _load_forbidden_patterns(self) -> Dict[str, List[str]]:
        return {
            "financial_advice": [
                r"\byou should invest\b",
                r"\bwe recommend buying\b",
                r"\bthis is a good investment\b",
                r"\bbuy now\b",
                r"\bsell now\b",
            ],
            "profit_guarantee": [
                r"\bguaranteed profit\b",
                r"\brisk[- ]?free\b",
                r"\bno risk\b",
                r"\b100% return\b",
                r"\bdouble your money\b",
            ],
            "price_prediction": [
                r"\bwill reach\b.*\$\d+",
                r"\bprice will go to\b",
                r"\btarget price\b",
                r"\bnext week\b.*\b\d+x\b",
            ],
            "scam_language": [
                r"\bget rich quick\b",
                r"\bsecret strategy\b",
                r"\binsider tip\b",
                r"\bguaranteed income\b",
            ],
            "call_to_action": [
                r"\bjoin now\b",
                r"\bsign up\b",
                r"\bstart earning\b",
                r"\bclick here\b",
            ],
        }
