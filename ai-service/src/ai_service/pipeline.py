"""Ties the steps together: facts (cache or LLM) -> match -> (judge if unclear) -> verdict.

  summary (cache: exact key -> FAISS -> else LLM) -> embedding match vs goal
      -> related: allow / unrelated: block / unclear: LLM judge

MVP assumes an LLM is available. If every provider fails, the page is allowed and
rechecked later. (A no-LLM "basic mode" is designed and parked: board frame 15,
.plans/architecture/future/basic-mode/.)

Board: MVP frame 4; full board frames 5 and 14.
"""

import logging

from pydantic import ValidationError

from .facts_cache import get_facts
from .judge import judge
from .llm import AllProvidersExhausted
from .matcher import match
from .schemas import Goal, PageData, Verdict
from .services import Services

log = logging.getLogger(__name__)

# Spec §5.7, last step: when the AI can't answer, allow the page and recheck later.
RECHECK = Verdict(
    decision="allow",
    reason="Couldn't check this page right now. It will be rechecked.",
    source="fallback",
)


def classify(page: PageData, goal: Goal, s: Services) -> Verdict:
    """Return allow/block for this page against this goal."""
    try:
        facts, facts_vec = get_facts(page, s.llm, s.embedder, s.index, s.engine, s.settings)
    except (AllProvidersExhausted, ValidationError) as e:
        log.warning("Describer failed, allowing page: %s", e)
        return RECHECK

    # Cheap first pass: local embeddings, no LLM call.
    result = match(facts_vec, s.goal_vectors.get(goal), s.settings)
    if result.band == "related":
        return Verdict(decision="allow", reason=f"Fits your goal: {facts.summary}.",
                       source="embedding", similarity=result.similarity)
    if result.band == "unrelated":
        return Verdict(decision="block", reason=f"Not part of your goal: {facts.summary}.",
                       source="embedding", similarity=result.similarity)

    # Only the unclear band pays for an LLM judge call.
    try:
        return judge(facts, goal, result.similarity, s.llm)
    except (AllProvidersExhausted, ValidationError) as e:
        log.warning("Judge failed, allowing page: %s", e)
        return RECHECK
