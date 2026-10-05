from typing import List, Optional
import numpy as np
from backend.app.embeddings.embedder import embedder
from backend.app.vector_db.vector_store import vector_store
from backend.app.models.schemas import (
    ArticleAnalysisResult, EvidencePassage, RAGResponse
)

class RAGEvidenceEngine:
    def index_articles(self, articles_analysis: List[ArticleAnalysisResult]):
        vector_store.clear()
        
        all_sentences = []
        all_metadata = []

        for art in articles_analysis:
            for s in art.sentences:
                all_sentences.append(s.text)
                all_metadata.append({
                    "source": art.source,
                    "article_title": art.title,
                    "sentence_idx": s.sentence_idx,
                    "framing": s.primary_frame,
                    "sentiment": s.sentiment_label,
                    "loaded_terms": [span.term for span in s.loaded_spans]
                })

        if all_sentences:
            embeds = embedder.encode(all_sentences)
            vector_store.add_vectors(embeds, all_sentences, all_metadata)

    def retrieve_evidence(
        self,
        query: str,
        target_sources: Optional[List[str]] = None,
        top_k: int = 4
    ) -> RAGResponse:
        query_vec = embedder.encode([query])[0]

        filter_fn = None
        if target_sources:
            filter_fn = lambda m: m.get("source") in target_sources

        raw_results = vector_store.similarity_search(query_vec, top_k=top_k, filter_fn=filter_fn)

        passages = []
        for r in raw_results:
            meta = r["metadata"]
            passages.append(EvidencePassage(
                source=meta["source"],
                article_title=meta["article_title"],
                sentence_text=r["document"],
                similarity_score=r["similarity_score"],
                framing=meta["framing"],
                sentiment=meta["sentiment"],
                loaded_terms=meta["loaded_terms"]
            ))

        # Contrastive synthesis explanation
        if len(passages) >= 2:
            sources_found = list({p.source for p in passages})
            explanation = (
                f"Retrieved {len(passages)} cross-source evidence passages across {len(sources_found)} outlets ({', '.join(sources_found)}). "
                f"Coverage shows contrasting perspectives: while '{passages[0].source}' emphasizes {passages[0].framing} framing ({passages[0].sentiment} tone), "
                f"'{passages[1].source}' frames the topic through {passages[1].framing} ({passages[1].sentiment} tone)."
            )
        elif len(passages) == 1:
            explanation = f"Found relevant evidence in '{passages[0].source}' highlighting {passages[0].framing} framing."
        else:
            explanation = "No matching evidence passages found in the current indexed vector store."

        return RAGResponse(
            query=query,
            retrieved_evidence=passages,
            contrastive_explanation=explanation
        )

rag_engine = RAGEvidenceEngine()
