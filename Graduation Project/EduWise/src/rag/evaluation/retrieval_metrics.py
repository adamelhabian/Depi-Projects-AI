# Retrieval evaluation

from rag.embeddings.embedder import TextEmbedder
from rag.vector_store.faiss_store import FaissVectorStore


def evaluate_retrieval_context(
    query: str,
    vector_store: FaissVectorStore,
    embedder: TextEmbedder,
    top_k: int = 5,
) -> dict[str, object]:

    query_vec = embedder.encode([query])
    semantic_hits = vector_store.search(query_vec, top_k=top_k)

    semantic_scores = [
        round(score, 4)
        for _, score in semantic_hits
    ]

    semantic_context = "\n\n---\n\n".join(
        text for text, _ in semantic_hits
    )

    return {
        "query": query,
        "retrieved_count": len(semantic_hits),
        "similarity_scores": semantic_scores,
        "average_similarity": (
            round(sum(semantic_scores) / len(semantic_scores), 4)
            if semantic_scores else 0.0
        ),
        "context_chars": len(semantic_context),
    }