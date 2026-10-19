"""Data shapes that flow through the pipeline.

PageData  (from the extension's content script)
   -> ContentFacts  (what the page IS; shareable across users)
   -> MatchResult   (how close it is to this user's goal)
   -> Verdict       (allow or block, and why)
"""

from typing import Literal

from pydantic import BaseModel, Field


class YouTubeData(BaseModel):
    video_id: str
    channel: str = ""
    tags: list[str] = Field(default_factory=list)
    category: str = ""
    description: str = ""


class PageData(BaseModel):
    """What the content script extracts from the page (spec §5.4, step 2)."""

    url: str
    title: str = ""
    meta_description: str = ""
    headings: list[str] = Field(default_factory=list)
    text_excerpt: str = ""
    youtube: YouTubeData | None = None


class Goal(BaseModel):
    """What the user is trying to do right now, plus their onboarding profile."""

    text: str
    profile: str = ""


ContentKind = Literal["educational", "entertainment", "news", "tool", "social", "other"]


class ContentFacts(BaseModel):
    """A short, user-independent description of the content (spec §5.5)."""

    summary: str  # e.g. "Minecraft survival gameplay, casual entertainment"
    topics: list[str]
    kind: ContentKind


MatchBand = Literal["related", "unrelated", "unclear"]


class MatchResult(BaseModel):
    similarity: float
    band: MatchBand


class Verdict(BaseModel):
    decision: Literal["allow", "block"]
    reason: str
    # Which step made the call. extracted / nearest = basic mode (spec §5.9), no LLM.
    source: Literal["embedding", "llm", "extracted", "nearest", "fallback"]
    similarity: float | None = None  # None when no goal match ran (e.g. fallback)
