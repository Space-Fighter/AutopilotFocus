"""The LLM provider chain: same-tier models tried in order (spec §5.6).

Board frame 3: "LLM provider chain (A -> B -> C when a quota runs out)".
"""

import json
import logging
import os

from openai import APIConnectionError, APIStatusError, OpenAI

from .config import ProviderConfig

log = logging.getLogger(__name__)


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

    def complete_json(self, system: str, user: str) -> dict:
        """Send one chat request, asking for a JSON object back, and return it parsed.

        Try each provider in order. On a rate limit, quota or connection error,
        move to the next one. Raise AllProvidersExhausted if none succeed.
        """
        errors: list[str] = []
        for provider, client in self._clients:
            try:
                response = client.chat.completions.create(
                    model=provider.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    response_format={"type": "json_object"},  # the prompt must mention "JSON"
                    temperature=0,  # least random: same input, same answer
                )
                return json.loads(response.choices[0].message.content)
            except APIStatusError as e:
                # 429 = rate limit or quota, 5xx = provider broken: try the next one.
                # Anything else (400 bad request, 401 bad key) is our bug, so fail loudly.
                if e.status_code != 429 and e.status_code < 500:
                    raise
                errors.append(f"{provider.name}: HTTP {e.status_code}")
            except APIConnectionError as e:  # also covers timeouts
                errors.append(f"{provider.name}: {type(e).__name__}")
            except json.JSONDecodeError:
                errors.append(f"{provider.name}: returned invalid JSON")
            log.warning("LLM provider failed, trying next: %s", errors[-1])

        raise AllProvidersExhausted("; ".join(errors))
