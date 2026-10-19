"""Cheap first pass: compares content facts with the user's goal using embeddings, no LLM call.

Board frame 3: "Goal matcher (similarity thresholds)". Frame 5: "Embedding match vs goal".
"""

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


def match(
    facts: ContentFacts, goal: Goal, embedder: Embedder, settings: Settings, basic: bool = False
) -> MatchResult:
    """Score facts against the goal and put the score in a band: related / unrelated / unclear.

    basic=True uses the basic-mode thresholds (extracted summaries may score differently).
    """
    # Step 0 shortcut: the goal is re-embedded every call. Later, cache its vector per session.
    similarity = cosine(embedder.embed(facts_text(facts)), embedder.embed(goal_text(goal)))

    related = settings.basic_related_threshold if basic else settings.related_threshold
    unrelated = settings.basic_unrelated_threshold if basic else settings.unrelated_threshold
    if similarity >= related:
        band = "related"
    elif similarity <= unrelated:
        band = "unrelated"
    else:
        band = "unclear"  # only this band costs an LLM judge call

    return MatchResult(similarity=similarity, band=band)
