# Dense semantic retrieval
# يستقبل سؤال المستخدم، يحوّله إلى Embedding، وبعدها يبحث في FAISS عن أكثر الـ chunks تشابهًا مع السؤال.

from rag.embeddings.embedder import TextEmbedder
from rag.vector_store.base import BaseVectorStore

class SemanticRetriever:
    def __init__(self, vector_store: BaseVectorStore, embedder: TextEmbedder) -> None:
        self.vector_store = vector_store
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = 5) -> str:
        if not query.strip():
            raise ValueError("Query cannot be empty.")
        query_vec = self.embedder.encode([query],task_type="RETRIEVAL_QUERY")
        hits = self.vector_store.search(query_vec, top_k=top_k)
        return "\n\n---\n\n".join(text for text, _ in hits)