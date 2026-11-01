"""Get ContentFacts for a page, calling the LLM only for pages we haven't described yet.

  1. exact key in Postgres?        -> reuse the stored summary   (no LLM)
  2. FAISS: similar page (>= 0.95)? -> reuse that page's summary   (no LLM)
  3. otherwise                     -> LLM describes it, then save it for next time

Returns the facts AND the summary vector, so a cache hit never re-embeds the summary.

Board: full board frame 14, steps 2-5; frame 10 "content_facts".
"""

import numpy as np
from sqlalchemy import Engine

from .config import Settings
from .describer import describe_content
from .embedder import Embedder
from .llm import ProviderChain
from .matcher import facts_text
from .models import ContentFactsRow
from .schemas import ContentFacts, PageData
from .summary_index import SummaryIndex


def row_to_facts(row: ContentFactsRow) -> tuple[ContentFacts, np.ndarray]:
    facts = ContentFacts(summary=row.summary, topics=row.topics, kind=row.kind)
    return facts, np.asarray(row.summary_vec, dtype=np.float32)


# YOU TYPE #9
def get_facts(
    page: PageData,
    llm: ProviderChain,
    embedder: Embedder,
    index: SummaryIndex,
    engine: Engine,
    settings: Settings,
) -> tuple[ContentFacts, np.ndarray]:
    """Return (facts, summary_vec) for this page: from the cache when possible, else from the LLM.

    Raises what describe_content raises (AllProvidersExhausted, ValidationError) on a cache miss
    when the LLM fails; classify() already handles those.
    """
    raise NotImplementedError("YOU TYPE #9")
