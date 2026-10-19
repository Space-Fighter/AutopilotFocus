"""Ties the steps together: describe -> match -> (judge if unclear) -> verdict.

Two modes. Both use the embedding model to compare the page with the goal:

  NORMAL MODE  LLM summary  -> embedding match -> unclear? ask the LLM judge
  BASIC MODE   page's own title/meta/headings -> embedding match -> unclear? allow
               (later: copy the closest past case, spec §5.9 step 3)

What "basic" means: judging a page with NO LLM AT ALL. It is not "the free tier"
and not "embeddings instead of the judge". It runs in two situations:
  1. A free user's daily AI cap is used up: the Go API sends use_llm=False.
  2. Every LLM provider is down: describe_content fails, so classify switches to it.
Premium users only reach it in case 2.

Board: frame 5 (normal mode), frame 15 (basic mode). No caches yet (no Postgres or FAISS).
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

    use_llm=True  -> normal mode (LLM summary, LLM judge for unclear cases).
    use_llm=False -> basic mode, no LLM at all. The Go API sends False when a free
                     user's daily AI cap is used up. Normal mode also falls back to
                     basic mode by itself if the LLM describer fails.
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
    """Basic mode (spec §5.9): judge a page with NO LLM call at all.

    The summary comes from the page's own fields (extracted_facts), the embedding
    match is the same as normal mode, and there is no LLM judge for unclear cases.
    """
    facts = extracted_facts(page)
    # basic=True: "this summary was made without an LLM", so use the basic-mode thresholds.
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
