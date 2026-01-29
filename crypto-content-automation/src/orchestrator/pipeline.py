# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0

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
        language_router,
        publishers: List,
        auditor
    ):
        self.generator = generator
        self.verifier = verifier
        self.compliance = compliance
        self.editor = editor
        self.language_router = language_router
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

        # 4. Edit & optimize (base language: EN)
        ctx.final_text = self.editor.edit(ctx.verified_text)
        ctx.compute_hash()
        self.auditor.log("edited", ctx)

        # 5. Translate
        ctx.translations = self.language_router.translate_all(
            ctx.final_text,
            languages
        )
        self.auditor.log("translated", ctx)

        # 6. Publish per language
        for lang, text in ctx.translations.items():
            for publisher in self.publishers:
                publisher.publish(text, ctx.metadata, language=lang)

        ctx.published_at = datetime.utcnow()
        self.auditor.log("published", ctx)

        return ctx
        
