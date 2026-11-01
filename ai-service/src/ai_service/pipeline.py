"""Ties the steps together: describe -> match -> (judge if unclear) -> verdict.

  LLM summary -> embedding match -> related: allow / unrelated: block / unclear: LLM judge

MVP assumes an LLM is available. If every provider fails, the page is allowed and
rechecked later. (A no-LLM "basic mode" is designed and parked: board frame 15,
.plans/architecture/future/basic-mode/.)

Board: MVP frame 4; full board frame 5. No caches yet (no Postgres or FAISS).
"""

import logging

from pydantic import ValidationError

from .config import Settings
from .describer import describe_content
from .embedder import Embedder
from .judge import judge
from .llm import AllProvidersExhausted, ProviderChain
from .matcher import match
from .schemas import Goal, PageData, Verdict

log = logging.getLogger(__name__)

# Spec §5.7, last step: when the AI can't answer, allow the page and recheck later.
RECHECK = Verdict(
    decision="allow",
    reason="Couldn't check this page right now. It will be rechecked.",
    source="fallback",
)


def classify(
    page: PageData,
    goal: Goal,
    llm: ProviderChain,
    embedder: Embedder,
    settings: Settings,
) -> Verdict:
    """Return allow/block for this page against this goal."""
    try:
        facts = describe_content(page, llm)
    except (AllProvidersExhausted, ValidationError) as e:
        log.warning("Describer failed, allowing page: %s", e)
        return RECHECK

    # Cheap first pass: local embeddings, no LLM call.
    result = match(facts, goal, embedder, settings)
    if result.band == "related":
        return Verdict(decision="allow", reason=f"Fits your goal: {facts.summary}.",
                       source="embedding", similarity=result.similarity)
    if result.band == "unrelated":
        return Verdict(decision="block", reason=f"Not part of your goal: {facts.summary}.",
                       source="embedding", similarity=result.similarity)

    # Only the unclear band pays for an LLM judge call.
    try:
        return judge(facts, goal, result.similarity, llm)
    except (AllProvidersExhausted, ValidationError) as e:
        log.warning("Judge failed, allowing page: %s", e)
        return RECHECK
