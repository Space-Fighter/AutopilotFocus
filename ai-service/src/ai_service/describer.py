"""Asks the LLM what a page IS, independent of any user's goal (spec §5.4, step 5).

Board frame 3: "Content describer (LLM -> short facts)".
"""

from .llm import ProviderChain
from .schemas import ContentFacts, PageData

# YOU TYPE #4: the system prompt
DESCRIBE_SYSTEM_PROMPT = """TODO"""


# YOU TYPE #4
def build_describe_prompt(page: PageData) -> str:
    """Turn the extracted page data into the user message for the LLM."""
    raise NotImplementedError("YOU TYPE #4")


# YOU TYPE #4
def describe_content(page: PageData, llm: ProviderChain) -> ContentFacts:
    """Call the LLM and validate its JSON into ContentFacts."""
    raise NotImplementedError("YOU TYPE #4")
