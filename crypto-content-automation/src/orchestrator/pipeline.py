# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

from datetime import datetime
from typing import Dict, Any, List
import hashlib


class PipelineContext:
    def __init__(self, topic: str):
        self.topic = topic
        self.generated_text = None
        self.verified_text = None
        self.compliance_passed = False
        self.final_text = None
        self.translations: Dict[str, str] = {}
        self.metadata: Dict[str, Any] = {}
        self.content_hash = None
        self.created_at = datetime.utcnow()
        self.published_at = None

    def compute_hash(self):
        if self.final_text:
            self.content_hash = hashlib.sha256(
                self.final_text.encode("utf-8")
            ).hexdigest()


class ContentPipeline:

    def __init__(
        self,
        generator,
        verifier,
        compliance,
        editor,
        watermark,
        language_router,
        blockchain_anchor,
        publishers: List,
        auditor
    ):
        self.generator = generator
        self.verifier = verifier
        self.compliance = compliance
        self.editor = editor
        self.watermark = watermark
        self.language_router = language_router
        self.blockchain_anchor = blockchain_anchor
        self.publishers = publishers
        self.auditor = auditor

    def run(self, topic: str, languages: List[str] = ["en"]) -> PipelineContext:
        ctx = PipelineContext(topic)

        # 1. Generate
        ctx.generated_text = self.generator.generate(topic)
        self.auditor.log("generated", ctx)

        # 2. Fact check
        ctx.verified_text, sources = self.verifier.verify(ctx.generated_text)
        ctx.metadata["sources"] = sources
        self.auditor.log("verified", ctx)

        # 3. Compliance
        ctx.compliance_passed = self.compliance.validate(ctx.verified_text)
        if not ctx.compliance_passed:
            self.auditor.log("blocked_by_compliance", ctx)
            raise RuntimeError("Compliance check failed")

        # 4. Edit
        ctx.final_text = self.editor.edit(ctx.verified_text)
        ctx.compute_hash()
        self.auditor.log("edited", ctx)

        # 5. Legal watermark
        ctx.final_text = self.watermark.apply(ctx.final_text, ctx.content_hash)
        self.auditor.log("watermarked", ctx)

        # 6. Blockchain anchoring (Layer 10)
        ctx.metadata["blockchain_proof"] = self.blockchain_anchor.anchor(ctx.content_hash)
        self.auditor.log("anchored_on_chain", ctx)

        # 7. Multilanguage
        ctx.translations = self.language_router.translate_all(
            ctx.final_text,
            languages
        )
        self.auditor.log("translated", ctx)

        # 8. Publish
        for lang, text in ctx.translations.items():
            for publisher in self.publishers:
                publisher.publish(text, ctx.metadata, language=lang)

        ctx.published_at = datetime.utcnow()
        self.auditor.log("published", ctx)

        return ctx


# ---------- Abstract Interfaces ----------

class BaseGenerator:
    def generate(self, topic: str) -> str:
        raise NotImplementedError


class BaseVerifier:
    def verify(self, text: str):
        """Return (verified_text, sources[])"""
        raise NotImplementedError


class BaseCompliance:
    def validate(self, text: str) -> bool:
        raise NotImplementedError


class BaseEditor:
    def edit(self, text: str) -> str:
        raise NotImplementedError


class BaseWatermark:
    def apply(self, text: str, content_hash: str) -> str:
        raise NotImplementedError


class BaseLanguageRouter:
    def translate_all(self, text: str, languages: List[str]) -> Dict[str, str]:
        raise NotImplementedError


class BaseBlockchainAnchor:
    def anchor(self, content_hash: str) -> Dict[str, Any]:
        raise NotImplementedError


class BasePublisher:
    def publish(self, text: str, metadata: Dict[str, Any], language: str):
        raise NotImplementedError


class BaseAuditor:
    def log(self, stage: str, ctx: PipelineContext):
        raise NotImplementedError
        
        
