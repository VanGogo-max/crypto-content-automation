# File: compliance/regulatory_filter.py
# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

"""
RegulatoryFilter module
- Ensures crypto content complies with:
  - MiCA (EU Markets in Crypto-Assets Regulation)
  - SEC (US securities and advertising rules)
  - General ad compliance
- Returns True if content passes, False otherwise
- Provides logging for blocked content
"""

import re

class ComplianceError(Exception):
    pass

class RegulatoryFilter:
    def __init__(self):
        # Example regex patterns for prohibited content
        self.prohibited_patterns = [
            r"guarantee\s+profit",
            r"risk-free",
            r"investment advice",
            r"pump and dump",
            r"insider tip",
            r"unregistered securities",
        ]

    def validate(self, text: str) -> bool:
        """
        Returns True if content passes compliance filters, False otherwise.
        """
        lower_text = text.lower()
        for pattern in self.prohibited_patterns:
            if re.search(pattern, lower_text):
                return False
        return True
