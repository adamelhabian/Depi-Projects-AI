# Vector store interface

# يحدد العقد (Contract) اللي لازم أي Vector Store implementation يلتزم بيه.

# مثلًا ممكن تستخدم:
# - FAISS
# - ChromaDB
# - Qdrant
# كل implementation لازم توفر نفس الدوال.

from abc import ABC, abstractmethod
import numpy as np

class BaseVectorStore(ABC):
    @abstractmethod
    def add(self, vectors: np.ndarray, texts: list[str]) -> None:
        pass

    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int) -> list[tuple[str, float]]:
        """Returns (text, similarity_score), sorted by descending similarity."""
        pass