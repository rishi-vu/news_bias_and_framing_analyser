import numpy as np
from typing import List, Dict, Any
from sklearn.cluster import AgglomerativeClustering
from backend.app.embeddings.embedder import embedder
from backend.app.models.schemas import ArticleInput

class EventClusterer:
    def __init__(self, distance_threshold: float = 0.45):
        # distance_threshold 0.45 corresponds to cosine similarity >= 0.55
        self.distance_threshold = distance_threshold

    def cluster_articles(self, articles: List[ArticleInput]) -> List[Dict[str, Any]]:
        if not articles:
            return []
        if len(articles) == 1:
            return [{
                "cluster_id": "cluster_0",
                "event_title": articles[0].title,
                "article_indices": [0],
                "articles": [articles[0]],
                "sources": [articles[0].source],
                "cohesion_score": 1.0
            }]

        # Create combined representation: title (high weight) + first 200 words
        representations = [
            f"{a.title}. {' '.join(a.content.split()[:150])}" for a in articles
        ]

        embeddings = embedder.encode(representations)

        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-9
        norm_embeddings = embeddings / norms

        try:
            # Agglomerative clustering with cosine distance metric
            clustering = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=self.distance_threshold,
                metric="cosine",
                linkage="average"
            )
            labels = clustering.fit_predict(norm_embeddings)
        except Exception:
            # Fallback if scikit-learn linkage fails on tiny sets
            labels = np.zeros(len(articles), dtype=int)

        clusters = {}
        for idx, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = {
                    "cluster_id": f"cluster_{label}",
                    "article_indices": [],
                    "articles": [],
                    "sources": [],
                }
            clusters[label]["article_indices"].append(idx)
            clusters[label]["articles"].append(articles[idx])
            clusters[label]["sources"].append(articles[idx].source)

        results = []
        for label, data in clusters.items():
            # Representative title: choose the one closest to cluster centroid
            cluster_embeds = norm_embeddings[data["article_indices"]]
            centroid = np.mean(cluster_embeds, axis=0)
            sims = np.dot(cluster_embeds, centroid)
            best_idx = np.argmax(sims)
            rep_article = data["articles"][best_idx]

            results.append({
                "cluster_id": data["cluster_id"],
                "event_title": rep_article.title,
                "article_indices": data["article_indices"],
                "articles": data["articles"],
                "sources": list(set(data["sources"])),
                "cohesion_score": round(float(np.mean(sims)), 3)
            })

        return results

event_clusterer = EventClusterer()
