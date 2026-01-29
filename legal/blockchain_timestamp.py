# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0

import hashlib
from datetime import datetime


class BlockchainTimestamp:
    """
    Anchors content hash into a blockchain transaction for immutable proof of existence.
    This class is chain-agnostic (Ethereum, Bitcoin, etc.)
    """

    def __init__(self, chain_client):
        self.chain = chain_client

    def anchor(self, content_hash: str) -> dict:
        """
        Writes hash to blockchain and returns transaction proof.
        """
        tx_hash = self.chain.write_hash(content_hash)

        return {
            "content_hash": content_hash,
            "tx_hash": tx_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "chain": self.chain.name
        }


class BaseChainClient:
    name = "undefined"

    def write_hash(self, content_hash: str) -> str:
        raise NotImplementedError
