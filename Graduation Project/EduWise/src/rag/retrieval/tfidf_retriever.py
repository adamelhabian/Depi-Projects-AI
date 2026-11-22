# TF-IDF baseline

# OPTIONAL  

# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# class TfidfRetriever:
#     def __init__(self, chunks: list[str], max_features: int = 15000) -> None:
#         self.chunks = chunks
#         self.vectorizer = TfidfVectorizer(
#             stop_words="english",
#             max_features=max_features,
#             ngram_range=(1, 2),
#         )
#         self.matrix = self.vectorizer.fit_transform(chunks) if chunks else None

#     def retrieve(self, query: str, top_k: int = 3) -> str:
#         if not self.chunks or self.matrix is None:
#             return ""
#         query_vec = self.vectorizer.transform([query])
#         scores = cosine_similarity(query_vec, self.matrix).flatten()
#         k = min(top_k, len(self.chunks))
#         top_idx = np.argsort(scores)[::-1][:k]
#         return "\n\n".join(self.chunks[i] for i in top_idx)