"""FAISS index over page vectors: "have we already described a page like this one?"

FAISS keeps only vectors + 64-bit IDs, in memory. The IDs are content_facts.id, so a search
result points straight at a Postgres row. Postgres stores every vector too, so the index is
rebuilt from it on every startup (load_from_db) and can always be thrown away.

Board: full board frame 14, step 3 "FAISS: close stored vector?".
"""

import faiss
import numpy as np
from sqlalchemy import Engine
from sqlmodel import select

from .db import new_session
from .models import EMBEDDING_DIM, ContentFactsRow


class SummaryIndex:
    def __init__(self) -> None:
        # IndexFlatIP: exact search by inner product (= cosine, because our vectors have length 1).
        # IndexIDMap2: lets us attach our own IDs (content_facts.id) instead of 0, 1, 2, ...
        self._index = faiss.IndexIDMap2(faiss.IndexFlatIP(EMBEDDING_DIM))

    def __len__(self) -> int:
        return self._index.ntotal

    def load_from_db(self, engine: Engine) -> None:
        """Rebuild the index from every row in content_facts (called once at startup)."""
        with new_session(engine) as db:
            rows = db.exec(select(ContentFactsRow.id, ContentFactsRow.page_vec)).all()
        self._index.reset()
        if rows:
            ids = np.array([r.id for r in rows], dtype=np.int64)
            vecs = np.vstack([r.page_vec for r in rows]).astype(np.float32)
            self._index.add_with_ids(vecs, ids)

    # YOU TYPE #8
    def add(self, row_id: int, page_vec: np.ndarray) -> None:
        """Add one page vector under its content_facts.id."""
        raise NotImplementedError("YOU TYPE #8")

    # YOU TYPE #8
    def search(self, page_vec: np.ndarray) -> tuple[int, float] | None:
        """Return (content_facts.id, similarity) of the closest stored page, or None if empty."""
        raise NotImplementedError("YOU TYPE #8")
