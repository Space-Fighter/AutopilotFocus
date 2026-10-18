"""The LLM provider chain: same-tier models tried in order (spec §5.6).

Board frame 3: "LLM provider chain (A -> B -> C when a quota runs out)".
"""

import json
import os

from openai import OpenAI

from .config import ProviderConfig


class AllProvidersExhausted(Exception):
    """Every provider failed or is rate-limited. The caller falls back (spec §5.7)."""


class ProviderChain:
    def __init__(self, providers: list[ProviderConfig], timeout_s: float):
        # One OpenAI-compatible client per provider that has an API key set.
        self._clients: list[tuple[ProviderConfig, OpenAI]] = []
        for p in providers:
            key = os.environ.get(p.api_key_env)
            if key:
                client = OpenAI(base_url=p.base_url, api_key=key, timeout=timeout_s, max_retries=0)
                self._clients.append((p, client))
        if not self._clients:
            raise RuntimeError("No LLM provider has an API key. Fill in ai-service/.env.")

    # YOU TYPE #3
    def complete_json(self, system: str, user: str) -> dict:
        """Send one chat request, asking for a JSON object back, and return it parsed.

        Try each provider in order. On a rate limit, quota or connection error,
        move to the next one. Raise AllProvidersExhausted if none succeed.
        """
        raise NotImplementedError("YOU TYPE #3")
