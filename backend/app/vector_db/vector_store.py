import numpy as np
from typing import List, Dict, Any, Optional

class VectorStore:
    def __init__(self):
        self.embeddings: List[np.ndarray] = []
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []

    def clear(self):
        self.embeddings = []
        self.documents = []
        self.metadata = []

    def add_vectors(self, vectors: np.ndarray, documents: List[str], metadata: List[Dict[str, Any]]):
        if len(vectors) != len(documents) or len(documents) != len(metadata):
            raise ValueError("Lengths of vectors, documents, and metadata must match.")
        
        for vec, doc, meta in zip(vectors, documents, metadata):
            self.embeddings.append(vec)
            self.documents.append(doc)
            self.metadata.append(meta)

    def similarity_search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        filter_fn: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        if not self.embeddings:
            return []

        all_vectors = np.array(self.embeddings)
        # Assuming normalized vectors (SentenceTransformer does this with normalize_embeddings=True)
        # Dot product equals cosine similarity
        query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-9)
        scores = np.dot(all_vectors, query_norm)

        results = []
        # Sort indices by score descending
        sorted_indices = np.argsort(scores)[::-1]

        for idx in sorted_indices:
            score = float(scores[idx])
            doc = self.documents[idx]
            meta = self.metadata[idx]

            if filter_fn and not filter_fn(meta):
                continue

            results.append({
                "document": doc,
                "metadata": meta,
                "similarity_score": round(score, 4)
            })

            if len(results) >= top_k:
                break

        return results

vector_store = VectorStore()
