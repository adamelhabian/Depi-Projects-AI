
# مسؤول عن:
# - تخزين الـ embeddings باستخدام FAISS.
# - ربط كل vector بالـ text الأصلي.
# - البحث عن أقرب chunks باستخدام similarity.
# - إرجاع أفضل النتائج مرتبة حسب التشابه.

# FAISS indexing and semantic search

import json
from pathlib import Path

import faiss
import numpy as np

from rag.vector_store.base import BaseVectorStore
from config.settings import settings


class FaissVectorStore(BaseVectorStore):

    def __init__(self, dimension: int) -> None:
        if dimension <= 0:
            raise ValueError("Vector dimension must be positive.")

        self.dimension = dimension
        self._index = faiss.IndexFlatIP(dimension)
        self._texts: list[str] = []

    def add(self, vectors: np.ndarray, texts: list[str]) -> None:
        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError("Invalid vector dimensions.")

        if len(vectors) != len(texts):
            raise ValueError(
                "Number of vectors must match number of text chunks."
            )

        if len(vectors) == 0:
            return

        if not np.isfinite(vectors).all():
            raise ValueError("Vectors contain invalid values.")

        if not all(isinstance(text, str) and text.strip() for text in texts):
            raise ValueError("All text chunks must be non-empty strings.")

        norm_vectors = vectors.astype("float32").copy()

        faiss.normalize_L2(norm_vectors)

        self._index.add(norm_vectors)
        self._texts.extend(texts)

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
    ) -> list[tuple[str, float]]:

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        if query_vector.ndim not in (1, 2):
            raise ValueError("Query vector must be 1D or 2D.")

        if query_vector.size != self.dimension:
            raise ValueError("Query vector dimension mismatch.")

        if not np.isfinite(query_vector).all():
            raise ValueError("Query vector contains invalid values.")

        if self._index.ntotal == 0:
            return []

        q_vec = query_vector.astype("float32").copy()

        if q_vec.ndim == 1:
            q_vec = q_vec.reshape(1, -1)

        faiss.normalize_L2(q_vec)

        k = min(top_k, self._index.ntotal)

        scores, indices = self._index.search(q_vec, k)

        results: list[tuple[str, float]] = []

        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(self._texts):
                results.append(
                    (self._texts[idx], float(score))
                )

        return results

    def save(self, name: str = "faiss_index") -> None:
        """Save the FAISS index and associated text chunks."""

        index_dir = settings.vector_indexes_dir
        index_dir.mkdir(parents=True, exist_ok=True)

        index_path = index_dir / f"{name}.faiss"
        texts_path = index_dir / f"{name}.json"

        if self._index.ntotal != len(self._texts):
            raise ValueError("FAISS index and text data are inconsistent.")

        faiss.write_index(self._index, str(index_path))

        texts_path.write_text(
            json.dumps(
                self._texts,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, name: str = "faiss_index") -> "FaissVectorStore":
        """Load a previously saved FAISS index and its text chunks."""

        index_dir = settings.vector_indexes_dir

        index_path = index_dir / f"{name}.faiss"
        texts_path = index_dir / f"{name}.json"

        if not index_path.exists() or not texts_path.exists():
            raise FileNotFoundError(
                f"Saved FAISS index '{name}' was not found."
            )

        index = faiss.read_index(str(index_path))

        texts = json.loads(
            texts_path.read_text(encoding="utf-8")
        )

        if not isinstance(texts, list) or not all(
            isinstance(text, str) for text in texts
        ):
            raise ValueError("Invalid saved text data.")

        if index.ntotal != len(texts):
            raise ValueError(
                "FAISS index and saved text data are inconsistent."
            )

        store = cls(dimension=index.d)

        store._index = index
        store._texts = texts

        return store