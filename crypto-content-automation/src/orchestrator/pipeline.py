# File: orchestrator/pipeline.py
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
orchestrator/pipeline.py

Enterprise-grade orchestration pipeline for:
- AI content generation
- Fact verification with sources
- Regulatory compliance filtering (MiCA / SEC / Ads)
- Editorial + SEO optimization
- Publishing (Blogger, Telegram)
- Audit logging
- SHA256 notarization
- On-chain proof on Ethereum Sepolia
- Fail-safe and traceable execution

Author: Crypto Content Automation System
License: Apache 2.0
"""

import os
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any

from generator.ai_generator import AIGenerator
from verifier.fact_checker import FactChecker
from compliance.regulatory_filter import RegulatoryFilter
from editor.content_editor import ContentEditor
from publisher.blogger_publisher import BloggerPublisher
from publisher.telegram_publisher import TelegramPublisher
from audit.audit_logger import AuditLogger
from legal.hash_notary import HashNotary
from legal.ethereum_client import EthereumClient

class PipelineError(Exception):
    pass


class ContentPipeline:
    def __init__(self):
        self._load_env()
        self._init_logging()
        self._init_modules()

    def _load_env(self):
        from dotenv import load_dotenv
        load_dotenv()

        self.eth_rpc_url = os.getenv("ETH_RPC_URL")
        self.eth_private_key = os.getenv("ETH_PRIVATE_KEY")
        self.eth_chain = os.getenv("ETH_CHAIN", "sepolia")

        if not self.eth_rpc_url or not self.eth_private_key:
            raise EnvironmentError("Missing ETH_RPC_URL or ETH_PRIVATE_KEY in .env")

    def _init_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        self.logger = logging.getLogger("ContentPipeline")

    def _init_modules(self):
        self.generator = AIGenerator()
        self.verifier = FactChecker()
        self.compliance = RegulatoryFilter()
        self.editor = ContentEditor()
        self.blogger = BloggerPublisher()
        self.telegram = TelegramPublisher()
        self.audit = AuditLogger()
        self.notary = HashNotary()
        self.eth_client = EthereumClient(
            rpc_url=self.eth_rpc_url,
            private_key=self.eth_private_key,
            network=self.eth_chain
        )

    def run(self, topic: str) -> Dict[str, Any]:
        trace_id = hashlib.sha256(f"{topic}{datetime.utcnow()}".encode()).hexdigest()[:16]
        self.logger.info(f"Starting pipeline | Trace ID: {trace_id}")

        try:
            # 1. Generate
            raw_content = self.generator.generate(topic)
            self.audit.log_step(trace_id, "generation", raw_content)

            # 2. Verify facts
            verified_content, sources = self.verifier.verify(raw_content)
            self.audit.log_step(trace_id, "verification", {"content": verified_content, "sources": sources})

            # 3. Compliance filter
            compliant_content = self.compliance.filter(verified_content)
            self.audit.log_step(trace_id, "compliance", compliant_content)

            # 4. Edit + SEO + watermark
            final_content = self.editor.edit(compliant_content, watermark=True)
            self.audit.log_step(trace_id, "editorial", final_content)

            # 5. Hash notarization
            sha256_hash = self.notary.hash(final_content)
            timestamp = datetime.utcnow().isoformat()
            self.audit.log_step(trace_id, "hash", {"sha256": sha256_hash, "timestamp": timestamp})

            # 6. On-chain notarization (Sepolia)
            tx_hash = self.eth_client.store_hash(sha256_hash, timestamp)
            self.audit.log_step(trace_id, "ethereum_tx", {"tx_hash": tx_hash})

            # 7. Publish
            blogger_url = self.blogger.publish(final_content)
            telegram_msg_id = self.telegram.publish(final_content)

            self.audit.log_step(trace_id, "publish", {
                "blogger_url": blogger_url,
                "telegram_id": telegram_msg_id
            })

            # 8. Final audit record
            result = {
                "trace_id": trace_id,
                "topic": topic,
                "sha256": sha256_hash,
                "ethereum_tx": tx_hash,
                "blogger_url": blogger_url,
                "telegram_id": telegram_msg_id,
                "sources": sources,
                "timestamp": timestamp,
                "network": self.eth_chain
            }

            self.audit.finalize(trace_id, result)
            self.logger.info(f"Pipeline completed successfully | Trace ID: {trace_id}")

            return result

        except Exception as e:
            self.logger.error(f"Pipeline failure | Trace ID: {trace_id} | Error: {str(e)}", exc_info=True)
            self.audit.log_error(trace_id, str(e))
            raise PipelineError(f"Pipeline execution failed: {e}") from e


if __name__ == "__main__":
    pipeline = ContentPipeline()
    output = pipeline.run("Future of On-Chain Identity and Zero-Knowledge Proofs")
    print(output)
            
