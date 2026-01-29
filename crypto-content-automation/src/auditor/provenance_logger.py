# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any

class ProvenanceLogger:
    """
    Records a tamper-proof audit trail for each content pipeline execution.
    Tracks:
    - content hash
    - topic
    - sources used
    - timestamps (creation, verification, publish)
    - pipeline versions / model versions
    """

    def __init__(self, log_dir: str = "audit_logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def log(self, stage: str, ctx):
        """
        Logs pipeline stage with metadata to a JSON file.
        """
        entry = {
            "stage": stage,
            "topic": ctx.topic,
            "timestamp": datetime.utcnow().isoformat(),
            "content_hash": getattr(ctx, "content_hash", None),
            "created_at": ctx.created_at.isoformat(),
            "published_at": getattr(ctx, "published_at", None),
            "sources": ctx.metadata.get("sources", []),
        }

        # Optional: add version info
        entry["pipeline_version"] = "1.0.0"
        entry["generator_version"] = getattr(ctx.generator, "version", "unknown")
        entry["verifier_version"] = getattr(ctx.verifier, "version", "unknown")
        entry["compliance_version"] = getattr(ctx.compliance, "version", "unknown")
        entry["editor_version"] = getattr(ctx.editor, "version", "unknown")

        # Write JSON log file
        filename = f"{ctx.topic.replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
        path = os.path.join(self.log_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)

        # Optionally, create a separate hash file for integrity
        hash_value = hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()
        with open(path + ".sha256", "w") as hf:
            hf.write(hash_value)

        print(f"[AUDIT] {stage} logged: {path} (hash: {hash_value})")
