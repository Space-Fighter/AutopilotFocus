"""Turns text into vectors so we can measure how similar two pieces of text are.

Board frame 3: "Embedder (bge-small, CPU)".
"""

import numpy as np
from fastembed import TextEmbedding


class Embedder:
    def __init__(self, model_name: str):
        # Downloads the model (~130 MB) on first use, then loads it from the local cache.
        self._model = TextEmbedding(model_name=model_name)

    def embed(self, text: str) -> np.ndarray:
        """Return a unit-length vector for `text`."""
        # embed() takes a batch and returns a generator; we pass a batch of one and take its first vector.
        vector = next(self._model.embed([text]))
        # Normalize so cosine() can be a plain dot product, even if a future model doesn't normalize.
        # np.linalg.norm(vector) gives us the vector's length
        # Dividing every nnumber by that length shrinks or stretches the vector untill its length is 1.
        # We normalize because when both vectors have length 1 cosine simillarity is just the dot product, so cosine stays one line
        return vector / np.linalg.norm(vector) 


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity of two unit-length vectors: 1.0 = same meaning, ~0 = unrelated."""
    return float(np.dot(a, b))
