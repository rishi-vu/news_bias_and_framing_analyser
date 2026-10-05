from typing import List, Dict, Any
from backend.app.models.schemas import (
    ArticleAnalysisResult, BiasIndicator, CrossSourceComparison,
    ClaimAlignment, OmissionItem, SpeakerBalanceStats
)

class ExplainabilityEngine:
    def generate_bias_indicators(
        self,
        articles: List[ArticleAnalysisResult],
        claim_alignments: List[ClaimAlignment],
        omissions: List[OmissionItem],
        quote_stats: List[SpeakerBalanceStats]
    ) -> List[BiasIndicator]:
        indicators: List[BiasIndicator] = []

        if len(articles) < 2:
            return indicators

        # 1. Framing Bias Indicator
        # Compare primary framing across sources
        framing_divergences = []
        for art in articles:
            top_frame = max(art.aggregate_framing.items(), key=lambda x: x[1])
            framing_divergences.append((art.source, top_frame[0], top_frame[1]))

        distinct_frames = set(f[1] for f in framing_divergences)
        if len(distinct_frames) > 1:
            frame_summary = ", ".join([f"'{s}': {f} ({int(p*100)}%)" for s, f, p in framing_divergences])
            indicators.append(BiasIndicator(
                indicator_type="Framing Bias",
                severity="High" if len(distinct_frames) >= 3 else "Medium",
                confidence=0.91,
                title="Cross-Source Framing Divergence",
                explanation=(
                    f"Outlets framed the identical event under fundamentally contrasting thematic lenses: {frame_summary}. "
                    "Rather than neutral presentation, each source contextualized the event to reinforce differing ideological priorities."
                ),
                evidence_examples=[
                    {"source": s, "frame": f, "weight": p} for s, f, p in framing_divergences
                ]
            ))

        # 2. Tone & Loaded Lexical Bias Indicator
        # Identify sources with disproportionately high loaded language density
        loaded_densities = [(art.source, art.loaded_language_density) for art in articles]
        loaded_densities.sort(key=lambda x: x[1], reverse=True)

        highest_loaded_source, highest_density = loaded_densities[0]
        lowest_loaded_source, lowest_density = loaded_densities[-1]

        if highest_density >= 2.0:
            # Collect sample loaded terms from the highest loaded source
            top_loaded_art = next(a for a in articles if a.source == highest_loaded_source)
            sample_loaded_spans = []
            for s in top_loaded_art.sentences:
                for span in s.loaded_spans:
                    sample_loaded_spans.append({
                        "term": span.term,
                        "category": span.category,
                        "severity": span.severity,
                        "sentence": s.text
                    })
                    if len(sample_loaded_spans) >= 4:
                        break
                if len(sample_loaded_spans) >= 4:
                    break

            indicators.append(BiasIndicator(
                indicator_type="Loaded Language",
                severity="High" if highest_density >= 3.5 else "Medium",
                confidence=0.88,
                title=f"Sensationalist & Loaded Language in '{highest_loaded_source}'",
                explanation=(
                    f"'{highest_loaded_source}' exhibited a loaded language density of {highest_density} instances per sentence, "
                    f"compared to '{lowest_loaded_source}' ({lowest_density} per sentence). The coverage employs emotionally charged metaphors "
                    "and pejorative characterizations instead of empirical, neutral terminology."
                ),
                evidence_examples=sample_loaded_spans
            ))

        # 3. Selective Reporting / Omission Bias Indicator
        if omissions:
            top_omission = omissions[0]
            indicators.append(BiasIndicator(
                indicator_type="Selective Omission",
                severity="High" if len(top_omission.omitted_by) > 1 else "Medium",
                confidence=0.85,
                title="Selective Fact & Context Omission",
                explanation=(
                    f"Significant informational divergence was detected. While {', '.join(top_omission.reported_by)} reported: "
                    f"\"{top_omission.representative_sentence[:120]}...\", this key aspect was completely omitted by {', '.join(top_omission.omitted_by)}, "
                    "affecting the reader's holistic perception of trade-offs."
                ),
                evidence_examples=[{
                    "aspect": top_omission.aspect_key,
                    "reported_by": top_omission.reported_by,
                    "omitted_by": top_omission.omitted_by,
                    "sentence": top_omission.representative_sentence
                }]
            ))

        # 4. Sourcing & Quoted Speaker Imbalance
        official_imbalances = []
        for qs in quote_stats:
            if qs.total_quotes > 0 and (qs.official_dominance_ratio >= 0.70 or qs.official_dominance_ratio == 0.0):
                official_imbalances.append(qs)

        if official_imbalances:
            imb = official_imbalances[0]
            role_desc = ", ".join([f"{k}: {v}" for k, v in imb.role_distribution.items()])
            indicators.append(BiasIndicator(
                indicator_type="Sourcing Imbalance",
                severity="Medium",
                confidence=0.82,
                title=f"One-Sided Voice Diversity in '{imb.source}'",
                explanation=(
                    f"'{imb.source}' demonstrates skewed sourcing. Total quoted speakers: {imb.total_quotes}, "
                    f"with breakdown: {role_desc}. The coverage lacks voice plurality, relying heavily on a single category of interest group."
                ),
                evidence_examples=[{
                    "source": imb.source,
                    "official_dominance": imb.official_dominance_ratio,
                    "top_speakers": imb.top_speakers
                }]
            ))

        # 5. Stance / Polarity Divergence Indicator
        sentiments = [(art.source, art.aggregate_sentiment.get("polarity", 0.0)) for art in articles]
        sentiments.sort(key=lambda x: x[1])
        if (sentiments[-1][1] - sentiments[0][1]) > 0.40:
            indicators.append(BiasIndicator(
                indicator_type="Tone Divergence",
                severity="High" if (sentiments[-1][1] - sentiments[0][1]) > 0.70 else "Medium",
                confidence=0.90,
                title="Bipolar Evaluative Stance",
                explanation=(
                    f"Stark polarity divide on the same news event: '{sentiments[-1][0]}' evaluated the outcome positively "
                    f"(polarity +{round(sentiments[-1][1], 2)}), whereas '{sentiments[0][0]}' framed it negatively "
                    f"(polarity {round(sentiments[0][1], 2)})."
                ),
                evidence_examples=[
                    {"source": s, "polarity": round(pol, 2)} for s, pol in sentiments
                ]
            ))

        return indicators

    def generate_synthesis(
        self,
        articles: List[ArticleAnalysisResult],
        indicators: List[BiasIndicator]
    ) -> str:
        if not articles:
            return "No articles provided for synthesis."

        sources = [a.source for a in articles]
        source_str = " and ".join(f"'{s}'" for s in sources)

        # Dominant frames per source
        frame_parts = []
        for art in articles:
            if art.aggregate_framing:
                top_frame = max(art.aggregate_framing.items(), key=lambda x: x[1])
                pct = int(top_frame[1] * 100)
                frame_parts.append(f"'{art.source}' led with {top_frame[0]} framing ({pct}%)")
        frame_str = "; ".join(frame_parts) if frame_parts else ""

        # Sentiment polarity per source
        sentiment_parts = []
        for art in articles:
            pol = art.aggregate_sentiment.get("polarity", 0.0)
            label = "positively" if pol > 0.1 else "negatively" if pol < -0.1 else "neutrally"
            sentiment_parts.append(f"'{art.source}' toned {label} (polarity {round(pol, 2)})")
        sentiment_str = "; ".join(sentiment_parts)

        # Loaded language
        max_loaded = max(articles, key=lambda a: a.loaded_language_density, default=None)

        # Indicator counts
        diverging_claims = next(
            (ind for ind in indicators if ind.indicator_type == "Framing Bias"), None
        )
        n_omissions = sum(1 for ind in indicators if ind.indicator_type == "Selective Omission")
        n_diverging = len([ind for ind in indicators if ind.indicator_type == "Tone Divergence"])

        summary = (
            f"Comparing {len(sources)} outlets — {source_str} — the analysis detected "
            f"{len(indicators)} bias indicator{'s' if len(indicators) != 1 else ''}. "
        )

        if frame_str:
            summary += f"Framing divergence: {frame_str}. "

        if sentiment_str:
            summary += f"Tone: {sentiment_str}. "

        if max_loaded and max_loaded.loaded_language_density >= 1.0:
            summary += (
                f"'{max_loaded.source}' showed the highest loaded language density "
                f"({max_loaded.loaded_language_density:.1f} charged terms per sentence). "
            )

        omission_ind = next((ind for ind in indicators if ind.indicator_type == "Selective Omission"), None)
        if omission_ind:
            summary += "Selective omissions were detected where factual aspects reported by one outlet were absent from others. "

        tone_ind = next((ind for ind in indicators if ind.indicator_type == "Tone Divergence"), None)
        if tone_ind:
            summary += f"A significant polarity split was detected in how outlets evaluated the same events. "

        summary = summary.strip()
        return summary if summary else "Analysis complete. No significant divergence detected across sources."


explainer = ExplainabilityEngine()
