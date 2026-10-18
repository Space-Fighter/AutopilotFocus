"""Turns text into vectors so we can measure how similar two pieces of text are.

Board frame 3: "Embedder (bge-small, CPU)".
"""

import numpy as np
from fastembed import TextEmbedding


class Embedder:
    def __init__(self, model_name: str):
        # Downloads the model (~130 MB) on first use, then loads it from the local cache.
        self._model = TextEmbedding(model_name=model_name)

    # YOU TYPE #1
    def embed(self, text: str) -> np.ndarray:
        """Return a unit-length vector for `text`."""
        raise NotImplementedError("YOU TYPE #1")


# YOU TYPE #1 (same step)
def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity of two unit-length vectors: 1.0 = same meaning, ~0 = unrelated."""
    raise NotImplementedError("YOU TYPE #1")
