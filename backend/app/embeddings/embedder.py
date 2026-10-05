import os
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


class TransformerEmbedder:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TransformerEmbedder, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if self._initialized:
            return
        self.model_name = model_name
        self.model = None
        self._initialized = True
        self._load_model_if_enabled()

    def _load_model_if_enabled(self):
        enable_heavy_model = os.getenv("USE_HEAVY_EMBEDDINGS", "false").lower() in {"1", "true", "yes", "on"}
        if not enable_heavy_model:
            logger.info("Heavy embedding model disabled for low-memory deployment; using TF-IDF fallback.")
            self.model = None
            return

        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({e}). Falling back to TF-IDF embedding.")
            self.model = None

    def ensure_loaded(self):
        if self.model is not None:
            return
        self._load_model_if_enabled()

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        self.ensure_loaded()

        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
                return np.array(embeddings, dtype=np.float32)
            except Exception as e:
                logger.error(f"Error encoding with SentenceTransformer: {e}")
                self.model = None

        # Fallback TF-IDF hash embedding (384 dimensions)
        return self._fallback_encode(texts)

    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        from sklearn.feature_extraction.text import HashingVectorizer
        vectorizer = HashingVectorizer(n_features=384, norm='l2', alternate_sign=False)
        mat = vectorizer.transform(texts).toarray()
        return mat.astype(np.float32)

    def cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

embedder = TransformerEmbedder()
