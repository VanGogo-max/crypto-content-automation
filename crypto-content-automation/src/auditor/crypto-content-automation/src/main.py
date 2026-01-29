# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0

from scheduler.job_runner import JobRunner
from pipeline.content_pipeline import ContentPipeline

from generator.ai_generator import AIGenerator
from verifier.fact_checker import FactChecker
from compliance.regulatory_filter import RegulatoryFilter
from editor.content_editor import ContentEditor
from publisher.telegram_publisher import TelegramPublisher
from publisher.blogger_publisher import BloggerPublisher
from auditor.provenance_logger import ProvenanceLogger


def run_full_pipeline():
    topic = "Bitcoin market outlook and macroeconomic impact"

    generator = AIGenerator()
    verifier = FactChecker()
    compliance = RegulatoryFilter()
    editor = ContentEditor()
    auditor = ProvenanceLogger()

    publishers = [
        TelegramPublisher(),
        BloggerPublisher()
    ]

    pipeline = ContentPipeline(
        generator=generator,
        verifier=verifier,
        compliance=compliance,
        editor=editor,
        publishers=publishers,
        auditor=auditor
    )

    ctx = pipeline.run(topic)
    print("Pipeline completed successfully.")
    print("Content hash:", ctx.content_hash)


if __name__ == "__main__":
    scheduler = JobRunner()

    # Всеки ден в 09:00 UTC
    scheduler.register_daily("09:00", run_full_pipeline)

    # Резервно – на всеки 12 часа
    scheduler.register_interval(720, run_full_pipeline)

    scheduler.run_forever()
