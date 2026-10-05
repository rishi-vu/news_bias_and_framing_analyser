from typing import List, Dict, Any
import numpy as np
from backend.app.embeddings.embedder import embedder
from backend.app.models.schemas import Claim, ClaimAlignment, ArticleAnalysisResult

class CrossSourceClaimComparator:
    def __init__(self, similarity_threshold: float = 0.72):  # raised from 0.65 for precision
        self.similarity_threshold = similarity_threshold

    def compare_claims_across_sources(
        self,
        articles_analysis: List[ArticleAnalysisResult]
    ) -> List[ClaimAlignment]:
        alignments: List[ClaimAlignment] = []

        if len(articles_analysis) < 2:
            return alignments

        # Collect claims tagged by source
        source_claims: Dict[str, List[Claim]] = {
            art.source: art.claims for art in articles_analysis
        }
        sources = list(source_claims.keys())

        # Pairwise comparison across sources
        seen_pairs = set()  # deduplicate
        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                source_a = sources[i]
                source_b = sources[j]

                claims_a = source_claims[source_a]
                claims_b = source_claims[source_b]

                if not claims_a or not claims_b:
                    continue

                texts_a = [c.text for c in claims_a]
                texts_b = [c.text for c in claims_b]

                embeds_a = embedder.encode(texts_a)
                embeds_b = embedder.encode(texts_b)

                # Similarity matrix between claims_a and claims_b
                sim_matrix = np.dot(embeds_a, embeds_b.T)

                # Track which claims_b have already been matched
                matched_b = set()

                # Sort by best similarity first so strong matches are picked up first
                pair_scores = [
                    (idx_a, int(np.argmax(sim_matrix[idx_a])), float(np.max(sim_matrix[idx_a])))
                    for idx_a in range(len(claims_a))
                ]
                pair_scores.sort(key=lambda x: -x[2])

                for idx_a, best_match_idx_b, max_sim in pair_scores:
                    claim_a = claims_a[idx_a]
                    claim_b = claims_b[best_match_idx_b]

                    # Deduplication: skip if this claim_b was already matched
                    pair_key = (source_a, claim_a.claim_id, source_b, claim_b.claim_id)
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)

                    if max_sim >= self.similarity_threshold:
                        # Determine concordant vs diverging using sentiment polarity delta
                        # from the articles' sentence-level sentiment scores
                        art_a = next((a for a in articles_analysis if a.source == source_a), None)
                        art_b = next((a for a in articles_analysis if a.source == source_b), None)

                        sent_score_a = 0.0
                        sent_score_b = 0.0
                        if art_a:
                            s = next((s for s in art_a.sentences if s.sentence_idx == claim_a.sentence_idx), None)
                            if s: sent_score_a = s.sentiment_score
                        if art_b:
                            s = next((s for s in art_b.sentences if s.sentence_idx == claim_b.sentence_idx), None)
                            if s: sent_score_b = s.sentiment_score

                        polarity_delta = abs(sent_score_a - sent_score_b)

                        # Diverging if opposite sentiment polarity AND same topic (high similarity)
                        if polarity_delta >= 0.35:
                            relation = "diverging"
                        else:
                            relation = "concordant"

                        alignments.append(ClaimAlignment(
                            claim_a=claim_a,
                            source_a=source_a,
                            claim_b=claim_b,
                            source_b=source_b,
                            similarity_score=round(max_sim, 3),
                            relation=relation
                        ))
                    else:
                        # Claim from source_a has no close counterpart in source_b
                        if best_match_idx_b not in matched_b:
                            alignments.append(ClaimAlignment(
                                claim_a=claim_a,
                                source_a=source_a,
                                claim_b=None,
                                source_b=source_b,
                                similarity_score=round(max_sim, 3),
                                relation="unsupported_in_b"
                            ))

        # Sort: diverging first, then concordant, then unsupported
        order = {"diverging": 0, "concordant": 1, "unsupported_in_b": 2}
        alignments.sort(key=lambda x: (order.get(x.relation, 3), -x.similarity_score))
        return alignments[:20]  # cap at 20 most relevant

claim_comparator = CrossSourceClaimComparator()
