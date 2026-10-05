from typing import List, Dict, Any, Tuple
from collections import defaultdict
import numpy as np

from backend.app.models.schemas import (
    ArticleInput, ArticleAnalysisResult, SentenceAnalysis,
    CrossSourceComparison, LoadedSpan
)
from backend.app.preprocessing.preprocessor import preprocessor
from backend.app.nlp_extraction.ner import ner_extractor
from backend.app.nlp_extraction.claim_extractor import claim_extractor
from backend.app.nlp_extraction.quote_extractor import quote_extractor
from backend.app.ml_analysis.sentiment import sentiment_analyzer
from backend.app.ml_analysis.stance import stance_detector
from backend.app.ml_analysis.framing import framing_detector
from backend.app.ml_analysis.emotion import emotion_detector
from backend.app.ml_analysis.loaded_language import loaded_language_detector
from backend.app.cross_source.claim_comparison import claim_comparator
from backend.app.cross_source.omission_detection import omission_detector
from backend.app.cross_source.quote_balance import quote_balance_analyzer
from backend.app.retrieval.rag_engine import rag_engine
from backend.app.explainability.explainer import explainer

class NewsAnalysisPipeline:
    def analyze_single_article(self, article: ArticleInput, index: int = 0) -> ArticleAnalysisResult:
        # Preprocessing: Clean and segment sentences
        raw_sentences = preprocessor.segment_sentences(article.content)
        if not raw_sentences:
            raw_sentences = [article.title]

        sentence_analyses: List[SentenceAnalysis] = []
        all_loaded_spans_count = 0

        # Run ML & extraction per sentence
        for idx, sent_text in enumerate(raw_sentences):
            # Sentiment
            sentiment_score, sentiment_label = sentiment_analyzer.analyze_sentence(sent_text)
            # Stance
            stance, stance_score = stance_detector.detect_stance(sent_text, sentiment_score)
            # Framing
            frame_scores, primary_frame = framing_detector.detect_framing(sent_text)
            # Emotion
            emotion_scores, primary_emotion = emotion_detector.detect_emotion(sent_text)
            # Loaded Language
            loaded_spans = loaded_language_detector.detect_loaded_spans(sent_text)
            has_loaded = len(loaded_spans) > 0
            all_loaded_spans_count += len(loaded_spans)

            sentence_analyses.append(SentenceAnalysis(
                sentence_idx=idx,
                text=sent_text,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                stance=stance,
                stance_score=stance_score,
                framing_scores=frame_scores,
                primary_frame=primary_frame,
                emotion_scores=emotion_scores,
                primary_emotion=primary_emotion,
                loaded_spans=loaded_spans,
                has_loaded_language=has_loaded
            ))

        # NLP Extractions at document level
        entities = ner_extractor.extract_entities(raw_sentences)
        claims = claim_extractor.extract_claims_from_sentences(raw_sentences)
        quotes = quote_extractor.extract_quotes_from_sentences(raw_sentences)

        # Compute Aggregates
        total_sents = len(sentence_analyses)
        avg_sentiment = round(float(np.mean([s.sentiment_score for s in sentence_analyses])), 3)
        pos_count = sum(1 for s in sentence_analyses if s.sentiment_label == "Positive")
        neg_count = sum(1 for s in sentence_analyses if s.sentiment_label == "Negative")
        neu_count = sum(1 for s in sentence_analyses if s.sentiment_label == "Neutral")

        aggregate_sentiment = {
            "polarity": avg_sentiment,
            "positive_ratio": round(pos_count / total_sents, 2),
            "negative_ratio": round(neg_count / total_sents, 2),
            "neutral_ratio": round(neu_count / total_sents, 2)
        }

        # Aggregate Framing
        frame_accum = defaultdict(float)
        for s in sentence_analyses:
            for f, val in s.framing_scores.items():
                frame_accum[f] += val
        aggregate_framing = {
            f: round(val / total_sents, 3) for f, val in frame_accum.items()
        }

        # Aggregate Emotion
        emotion_accum = defaultdict(float)
        for s in sentence_analyses:
            for emo, val in s.emotion_scores.items():
                emotion_accum[emo] += val
        aggregate_emotions = {
            emo: round(val / total_sents, 3) for emo, val in emotion_accum.items()
        }

        # Aggregate Stance
        support_count = sum(1 for s in sentence_analyses if s.stance == "Support")
        oppose_count = sum(1 for s in sentence_analyses if s.stance == "Oppose")
        neutral_stance_count = sum(1 for s in sentence_analyses if s.stance == "Neutral")
        aggregate_stance = {
            "support": round(support_count / total_sents, 2),
            "oppose": round(oppose_count / total_sents, 2),
            "neutral": round(neutral_stance_count / total_sents, 2)
        }

        # Loaded language density (terms per sentence)
        density = round(all_loaded_spans_count / max(1, total_sents), 2)

        # Voice diversity: unique roles / total possible roles (5)
        unique_roles = len(set(q.speaker_role for q in quotes))
        voice_diversity = round(unique_roles / 5.0, 2)

        return ArticleAnalysisResult(
            article_id=article.id or f"art_{index}",
            title=article.title,
            source=article.source,
            url=article.url or "",
            sentence_count=total_sents,
            sentences=sentence_analyses,
            entities=entities,
            claims=claims,
            quotes=quotes,
            aggregate_sentiment=aggregate_sentiment,
            aggregate_framing=aggregate_framing,
            aggregate_emotions=aggregate_emotions,
            aggregate_stance=aggregate_stance,
            loaded_language_density=density,
            speaker_voice_diversity=voice_diversity
        )

    def analyze_event_cross_source(
        self,
        articles: List[ArticleInput],
        event_topic: str = "Multi-Source Event Analysis"
    ) -> Tuple[List[ArticleAnalysisResult], CrossSourceComparison]:
        # 1. Analyze each article independently
        analyzed_articles = [
            self.analyze_single_article(art, idx) for idx, art in enumerate(articles)
        ]

        # 2. Index in Vector Store for Evidence Retrieval / RAG
        rag_engine.index_articles(analyzed_articles)

        # 3. Cross-Source Engine: Claims, Omissions, Quotes
        claim_alignments = claim_comparator.compare_claims_across_sources(analyzed_articles)
        omissions = omission_detector.detect_omissions(analyzed_articles)
        quote_stats = quote_balance_analyzer.analyze_quote_balance(analyzed_articles)

        # 4. Matrices for Framing and Sentiment divergence
        framing_matrix = {
            art.source: art.aggregate_framing for art in analyzed_articles
        }
        sentiment_matrix = {
            art.source: art.aggregate_sentiment for art in analyzed_articles
        }

        # 5. Explainability Engine: Bias Indicators & Synthesis
        bias_indicators = explainer.generate_bias_indicators(
            analyzed_articles, claim_alignments, omissions, quote_stats
        )
        synthesis = explainer.generate_synthesis(analyzed_articles, bias_indicators)

        sources = [art.source for art in analyzed_articles]

        comparison = CrossSourceComparison(
            event_title=event_topic,
            sources_analyzed=sources,
            framing_divergence_matrix=framing_matrix,
            sentiment_divergence_matrix=sentiment_matrix,
            claim_comparisons=claim_alignments,
            omissions=omissions,
            speaker_balance=quote_stats,
            bias_indicators=bias_indicators,
            synthesis_summary=synthesis
        )

        return analyzed_articles, comparison

pipeline = NewsAnalysisPipeline()
