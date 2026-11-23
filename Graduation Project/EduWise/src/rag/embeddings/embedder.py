# Generate text embeddings



import numpy as np
from google import genai
from google.genai import types

from config.settings import settings


class TextEmbedder:

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self.embedding_dimension = settings.embedding_dimension

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def encode(
        self,
        texts: list[str],
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> np.ndarray:

        if not texts:
            return np.empty(
                (0, self.embedding_dimension),
                dtype=np.float32,
            )

        all_vectors = []

        for text in texts:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=self.embedding_dimension,
                ),
            )

            all_vectors.append(response.embeddings[0].values)

        return np.asarray(all_vectors, dtype=np.float32)