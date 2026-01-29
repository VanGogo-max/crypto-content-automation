# File: legal/ethereum_client.py
# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0

import os
import time
from typing import Optional
from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account


class EthereumClientError(Exception):
    pass


class EthereumClient:
    def __init__(self, rpc_url: str, private_key: str, network: str = "sepolia"):
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.network = network

        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise EthereumClientError("Cannot connect to Ethereum RPC")

        self.account = Account.from_key(self.private_key)
        self.address = self.account.address
        self.chain_id = self._resolve_chain_id()

    def _resolve_chain_id(self) -> int:
        if self.network.lower() == "sepolia":
            return 11155111
        elif self.network.lower() == "mainnet":
            return 1
        else:
            raise EthereumClientError(f"Unsupported network: {self.network}")

    def _build_tx(self, data_hex: str):
        nonce = self.w3.eth.get_transaction_count(self.address)

        base_fee = self.w3.eth.get_block("latest").baseFeePerGas
        priority_fee = self.w3.to_wei(2, "gwei")
        max_fee = base_fee * 2 + priority_fee

        tx = {
            "from": self.address,
            "to": self.address,  # self-anchoring, data-only tx
            "value": 0,
            "nonce": nonce,
            "data": data_hex,
            "chainId": self.chain_id,
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee,
            "gas": 21000 + 8000,
            "type": 2
        }
        return tx

    def store_hash(self, sha256_hex: str, timestamp_iso: str) -> str:
        payload = f"{sha256_hex}|{timestamp_iso}"
        data_hex = self.w3.to_hex(text=payload)

        tx = self._build_tx(data_hex)
        signed = self.account.sign_transaction(tx)

        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        except Exception as e:
            raise EthereumClientError(f"Transaction send failed: {e}")

        return self._wait_for_receipt(tx_hash)

    def _wait_for_receipt(self, tx_hash, timeout: int = 180) -> str:
        start = time.time()
        while time.time() - start < timeout:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt and receipt.status == 1:
                    return tx_hash.hex()
                elif receipt and receipt.status == 0:
                    raise EthereumClientError("Transaction reverted on-chain")
            except TransactionNotFound:
                time.sleep(3)

        raise EthereumClientError("Transaction confirmation timeout")
