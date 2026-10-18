"""Cheap first pass: compares content facts with the user's goal using embeddings, no LLM call.

Board frame 3: "Goal matcher (similarity thresholds)". Frame 5: "Embedding match vs goal".
"""

from .config import Settings
from .embedder import Embedder, cosine
from .schemas import ContentFacts, Goal, MatchResult


# YOU TYPE #2
def facts_text(facts: ContentFacts) -> str:
    """Flatten ContentFacts into one string to embed."""
    raise NotImplementedError("YOU TYPE #2")


# YOU TYPE #2
def goal_text(goal: Goal) -> str:
    """Flatten the goal (and profile) into one string to embed."""
    raise NotImplementedError("YOU TYPE #2")


# YOU TYPE #2
def match(facts: ContentFacts, goal: Goal, embedder: Embedder, settings: Settings) -> MatchResult:
    """Score facts against the goal and put the score in a band: related / unrelated / unclear."""
    raise NotImplementedError("YOU TYPE #2")
