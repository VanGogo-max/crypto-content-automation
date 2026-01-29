# File: audit/audit_logger.py
# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

"""
Immutable audit logger with:
- JSONL append-only logs
- Per-day Merkle root
- Step-level hashing
- Trace ID support
- Finalization record
- Tamper-evident chaining (hash(prev) -> hash(curr))
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional


class AuditLoggerError(Exception):
    pass


class AuditLogger:
    def __init__(self, base_dir: str = "audit_logs"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    # ---------- Public API ----------

    def log_step(self, trace_id: str, step: str, payload: Any) -> None:
        record = self._build_record(trace_id, step, payload)
        self._append_record(record)

    def log_error(self, trace_id: str, error_message: str) -> None:
        record = self._build_record(trace_id, "error", {"message": error_message})
        self._append_record(record)

    def finalize(self, trace_id: str, summary: Dict[str, Any]) -> Dict[str, Any]:
        record = self._build_record(trace_id, "finalize", summary)
        self._append_record(record)
        merkle_root = self._compute_daily_merkle_root()
        return {"trace_id": trace_id, "daily_merkle_root": merkle_root}

    # ---------- Internals ----------

    def _build_record(self, trace_id: str, stage: str, payload: Any) -> Dict[str, Any]:
        ts = datetime.utcnow().isoformat()
        body = {
            "trace_id": trace_id,
            "stage": stage,
            "timestamp": ts,
            "payload": payload,
        }
        body_hash = self._sha256(json.dumps(body, ensure_ascii=False, sort_keys=True))
        body["record_hash"] = body_hash

        prev_hash = self._get_last_record_hash()
        body["prev_record_hash"] = prev_hash
        body["chain_hash"] = self._sha256(f"{prev_hash}{body_hash}")

        return body

    def _append_record(self, record: Dict[str, Any]) -> None:
        path = self._daily_log_path()
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            raise AuditLoggerError(f"Failed to append audit record: {e}")

    def _get_last_record_hash(self) -> str:
        path = self._daily_log_path()
        if not os.path.exists(path):
            return "0" * 64

        try:
            with open(path, "rb") as f:
                lines = f.read().splitlines()
                if not lines:
                    return "0" * 64
                last = json.loads(lines[-1].decode("utf-8"))
                return last.get("chain_hash", "0" * 64)
        except Exception:
            return "0" * 64

    def _daily_log_path(self) -> str:
        day = datetime.utcnow().strftime("%Y-%m-%d")
        return os.path.join(self.base_dir, f"audit_{day}.jsonl")

    def _sha256(self, data: str) -> str:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    # ---------- Merkle Root ----------

    def _compute_daily_merkle_root(self) -> Optional[str]:
        path = self._daily_log_path()
        if not os.path.exists(path):
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                hashes = [json.loads(line)["chain_hash"] for line in f if line.strip()]
            if not hashes:
                return None
            return self._merkle_root(hashes)
        except Exception as e:
            raise AuditLoggerError(f"Merkle root computation failed: {e}")

    def _merkle_root(self, leaves: List[str]) -> str:
        current = leaves[:]
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                combined = self._sha256(left + right)
                next_level.append(combined)
            current = next_level
        return current[0]
