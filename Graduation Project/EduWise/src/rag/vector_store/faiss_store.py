# FAISS indexing and search
# مسؤول عن:
# - تخزين الـ embeddings باستخدام FAISS.
# - ربط كل vector بالـ text الأصلي.
# - البحث عن أقرب chunks باستخدام similarity.
# - إرجاع أفضل النتائج مرتبة حسب التشابه.

import faiss
import numpy as np
from rag.vector_store.base import BaseVectorStore




class FaissVectorStore(BaseVectorStore):
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self._index = faiss.IndexFlatIP(dimension)
        self._texts: list[str] = []

    def add(self, vectors: np.ndarray, texts: list[str]) -> None:
        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError("Invalid vector dimensions.")

        if len(vectors) == 0:
            return
        if len(vectors) != len(texts):
            raise ValueError("Number of vectors must match number of text chunks.")
        norm_vectors = vectors.astype("float32").copy()
        faiss.normalize_L2(norm_vectors)
        self._index.add(norm_vectors)
        self._texts.extend(texts)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[tuple[str, float]]:
        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        if query_vector.ndim not in (1, 2):
            raise ValueError("Query vector must be 1D or 2D.")

        if query_vector.size != self.dimension:
            raise ValueError("Query vector dimension mismatch.")
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
                results.append((self._texts[idx], float(score)))
        return results