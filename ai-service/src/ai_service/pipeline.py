"""Ties the steps together: describe -> match -> (judge if unclear) -> verdict.

Board frame 5: the bottom half of "AI agent — verdict pipeline".
No caches yet (no Postgres or FAISS in Step 0).
"""

from .config import Settings
from .embedder import Embedder
from .llm import ProviderChain
from .schemas import Goal, PageData, Verdict


# YOU TYPE #6
def classify(
    page: PageData,
    goal: Goal,
    llm: ProviderChain,
    embedder: Embedder,
    settings: Settings,
) -> Verdict:
    """Return allow/block for this page against this goal."""
    raise NotImplementedError("YOU TYPE #6")
