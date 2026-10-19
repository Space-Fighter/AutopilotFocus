"""Ties the steps together: describe -> match -> (judge if unclear) -> verdict.

Board frame 5: the bottom half of "AI agent — verdict pipeline".
Board frame 15: basic mode, the same idea with no LLM (spec §5.9).
No caches yet (no Postgres or FAISS in Step 0).
"""

import logging

from pydantic import ValidationError

from .config import Settings
from .describer import describe_content, extracted_facts
from .embedder import Embedder
from .judge import judge
from .llm import AllProvidersExhausted, ProviderChain
from .matcher import match
from .schemas import Goal, PageData, Verdict

log = logging.getLogger(__name__)

# Spec §5.7, last step: when nothing can decide, allow the page and recheck later.
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
    use_llm: bool = True,
) -> Verdict:
    """Return allow/block for this page against this goal.

    use_llm=False is basic mode: the Go API sends it when a free user's daily AI cap is used up.
    """
    if not use_llm:
        return basic_classify(page, goal, embedder, settings)

    try:
        facts = describe_content(page, llm)
    except (AllProvidersExhausted, ValidationError) as e:
        log.warning("Describer failed, using basic mode: %s", e)
        return basic_classify(page, goal, embedder, settings)

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


def basic_classify(page: PageData, goal: Goal, embedder: Embedder, settings: Settings) -> Verdict:
    """Basic mode (spec §5.9): judge from the page's own fields, with no LLM call."""
    facts = extracted_facts(page)
    result = match(facts, goal, embedder, settings, basic=True)
    if result.band == "related":
        return Verdict(decision="allow", reason=f"Fits your goal: {facts.summary}.",
                       source="extracted", similarity=result.similarity)
    if result.band == "unrelated":
        return Verdict(decision="block", reason=f"Not part of your goal: {facts.summary}.",
                       source="extracted", similarity=result.similarity)

    # Step 3, closest past case (same user, similar page + goal), needs stored verdict
    # vectors in Postgres. Until that store exists, unclear pages are allowed.
    return RECHECK.model_copy(update={"similarity": result.similarity})
