import numpy as np
from typing import List, Dict
from backend.app.embeddings.embedder import embedder
from backend.app.models.schemas import OmissionItem, ArticleAnalysisResult

class OmissionDetector:
    def __init__(self, omission_threshold: float = 0.58):
        self.omission_threshold = omission_threshold

    def detect_omissions(
        self,
        articles_analysis: List[ArticleAnalysisResult]
    ) -> List[OmissionItem]:
        if len(articles_analysis) < 2:
            return []

        sources = [art.source for art in articles_analysis]
        omission_items: List[OmissionItem] = []

        # Build sentence pools for each source
        source_sentences: Dict[str, List[str]] = {}
        source_embeds: Dict[str, np.ndarray] = {}

        for art in articles_analysis:
            sents = [s.text for s in art.sentences if len(s.text.split()) >= 6]
            source_sentences[art.source] = sents
            source_embeds[art.source] = embedder.encode(sents) if sents else np.empty((0, 384))

        # Check each source's informative sentences against other sources
        processed_aspects = []

        for source_a in sources:
            sents_a = source_sentences[source_a]
            embeds_a = source_embeds[source_a]

            for idx_a, sent_a in enumerate(sents_a):
                # Filter out pure rhetorical opinions or generic transitions
                if len(sent_a.split()) < 8:
                    continue

                vec_a = embeds_a[idx_a]

                # Check if this sentence was already covered by an earlier aspect
                already_covered = False
                for prev_vec in processed_aspects:
                    if float(np.dot(vec_a, prev_vec)) > 0.80:
                        already_covered = True
                        break
                if already_covered:
                    continue

                reported_by = [source_a]
                omitted_by = []

                for other_source in sources:
                    if other_source == source_a:
                        continue
                    embeds_other = source_embeds[other_source]
                    if embeds_other.shape[0] == 0:
                        omitted_by.append(other_source)
                        continue

                    # Max similarity in other source's sentences
                    sims = np.dot(embeds_other, vec_a)
                    max_sim = float(np.max(sims))

                    if max_sim >= self.omission_threshold:
                        reported_by.append(other_source)
                    else:
                        omitted_by.append(other_source)

                # If at least one source omitted it, it represents an omission divergence
                if omitted_by:
                    processed_aspects.append(vec_a)
                    # Create concise aspect key
                    words = [w for w in sent_a.split() if len(w) > 4][:5]
                    aspect_key = " ".join(words)

                    # Compute salience based on numbers, entities, or length
                    has_numbers = any(char.isdigit() for char in sent_a)
                    salience = 0.85 if has_numbers else 0.72

                    omission_items.append(OmissionItem(
                        aspect_key=aspect_key,
                        description=f"Coverage regarding: '{sent_a[:90]}...'",
                        reported_by=reported_by,
                        omitted_by=omitted_by,
                        representative_sentence=sent_a,
                        salience_score=salience
                    ))

        # Sort omissions by salience descending
        omission_items.sort(key=lambda x: (len(x.omitted_by), x.salience_score), reverse=True)
        return omission_items[:8]  # top salient omissions

omission_detector = OmissionDetector()
