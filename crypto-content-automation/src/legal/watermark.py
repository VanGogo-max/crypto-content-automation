# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0

from datetime import datetime


class CopyrightWatermark:
    """
    Injects legal ownership and cryptographic trace into the content.
    """

    def __init__(self, owner: str, project: str):
        self.owner = owner
        self.project = project

    def apply(self, text: str, content_hash: str) -> str:
        stamp = f"""

---
© {datetime.utcnow().year} {self.owner}
Project: {self.project}
Content Hash (SHA256): {content_hash}
All rights reserved. Commercial use requires a valid license.
---
"""
        return text + stamp
