"""Get ContentFacts for a page, calling the LLM only for pages we haven't described yet.

  1. exact key in Postgres?        -> reuse the stored summary   (no LLM)
  2. FAISS: similar page (>= 0.95)? -> reuse that page's summary   (no LLM)
  3. otherwise                     -> LLM describes it, then save it for next time

Returns the facts AND the summary vector, so a cache hit never re-embeds the summary.

Board: full board frame 14, steps 2-5; frame 10 "content_facts".
"""

import logging

import numpy as np
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from .config import Settings
from .db import new_session
from .describer import describe_content
from .embedder import Embedder
from .llm import ProviderChain
from .matcher import facts_text
from .models import ContentFactsRow
from .page_identity import content_key, page_text
from .schemas import ContentFacts, PageData
from .summary_index import SummaryIndex

log = logging.getLogger(__name__)


def row_to_facts(row: ContentFactsRow) -> tuple[ContentFacts, np.ndarray]:
    facts = ContentFacts(summary=row.summary, topics=row.topics, kind=row.kind)
    return facts, np.asarray(row.summary_vec, dtype=np.float32)


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
    key = content_key(page)

    with new_session(engine) as db:
        # 1. Exact match: one indexed lookup on the UNIQUE content_key column.
        row = db.exec(select(ContentFactsRow).where(ContentFactsRow.content_key == key)).first()
        if row:
            log.info("cache hit (exact): %s", key)
            return row_to_facts(row)

        # 2. Similar page: embed the page's own text and ask FAISS for the closest stored page.
        page_vec = embedder.embed(page_text(page))
        hit = index.search(page_vec)
        if hit and hit[1] >= settings.cache_similarity_threshold:
            row = db.get(ContentFactsRow, hit[0])  # FAISS IDs are content_facts.id
            if row:
                log.info("cache hit (similar %.3f): %s ~ %s", hit[1], key, row.content_key)
                return row_to_facts(row)

    # 3. Miss: ask the LLM. This happens outside the `with` block so no DB connection is held
    #    open during a slow LLM call.
    facts = describe_content(page, llm)
    summary_vec = embedder.embed(facts_text(facts))

    with new_session(engine) as db:
        row = ContentFactsRow(
            content_key=key,
            summary=facts.summary,
            topics=facts.topics,
            kind=facts.kind,
            page_vec=page_vec,
            summary_vec=summary_vec,
        )
        db.add(row)
        try:
            db.commit()
        except IntegrityError:
            # Two requests described the same new page at the same time; the other one saved first.
            db.rollback()
            existing = db.exec(select(ContentFactsRow).where(ContentFactsRow.content_key == key)).one()
            return row_to_facts(existing)
        db.refresh(row)  # load the id Postgres generated
        index.add(row.id, page_vec)

    log.info("cache miss, described and saved: %s", key)
    return facts, summary_vec
