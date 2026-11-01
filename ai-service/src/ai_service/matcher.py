"""Cheap first pass: compares the page summary with the user's goal using embeddings, no LLM call.

Board frame 3: "Goal matcher (similarity thresholds)". Frame 5: "Embedding match vs goal".
"""

import numpy as np

from .config import Settings
from .embedder import Embedder, cosine
from .schemas import ContentFacts, Goal, MatchResult


def facts_text(facts: ContentFacts) -> str:
    """Flatten ContentFacts into one string to embed."""
    # `kind` is left out: only six values shared by every page, so it adds noise, not meaning.
    return f"{facts.summary}. Topics: {', '.join(facts.topics)}"


def goal_text(goal: Goal) -> str:
    """Flatten the goal (and profile) into one string to embed."""
    # The profile may pull all "student" content closer. If the eval shows that, drop it here
    # and let the LLM judge use the profile instead.
    if goal.profile:
        return f"{goal.text} (as a {goal.profile})"
    return goal.text


class GoalVectors:
    """Remembers each goal's vector, so a goal is embedded once, not on every page.

    While blocking is On the goal never changes, so every page after the first is a cache hit.
    """

    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder
        self._cache: dict[str, np.ndarray] = {}

    # YOU TYPE #10
    def get(self, goal: Goal) -> np.ndarray:
        """Return the vector for goal_text(goal): from the cache, or embed it and remember it."""
        raise NotImplementedError("YOU TYPE #10")


def match(facts_vec: np.ndarray, goal_vec: np.ndarray, settings: Settings) -> MatchResult:
    """Score the summary vector against the goal vector and put the score in a band."""
    similarity = cosine(facts_vec, goal_vec)

    if similarity >= settings.related_threshold:
        band = "related"
    elif similarity <= settings.unrelated_threshold:
        band = "unrelated"
    else:
        band = "unclear"  # only this band costs an LLM judge call

    return MatchResult(similarity=similarity, band=band)
