"""LLM judge for the "unclear" cases the embedding match can't decide.

Board frame 3: "Judges (verdict · appeal · Convince Me personas)". Only the verdict part for now.
"""

from .llm import ProviderChain
from .schemas import ContentFacts, Goal, Verdict

# YOU TYPE #5: the system prompt
JUDGE_SYSTEM_PROMPT = """TODO"""


# YOU TYPE #5
def judge(facts: ContentFacts, goal: Goal, similarity: float, llm: ProviderChain) -> Verdict:
    """Ask the LLM whether this content serves the goal; return an allow/block Verdict."""
    raise NotImplementedError("YOU TYPE #5")
