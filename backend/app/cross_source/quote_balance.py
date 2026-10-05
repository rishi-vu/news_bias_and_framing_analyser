from typing import List, Dict, Any
from collections import Counter
import numpy as np
from backend.app.models.schemas import SpeakerBalanceStats, ArticleAnalysisResult

class QuoteBalanceAnalyzer:
    def analyze_quote_balance(
        self,
        articles_analysis: List[ArticleAnalysisResult]
    ) -> List[SpeakerBalanceStats]:
        stats_list = []

        for art in articles_analysis:
            quotes = art.quotes
            total = len(quotes)

            role_counts = Counter()
            speaker_counts = Counter()

            for q in quotes:
                role_counts[q.speaker_role] += 1
                speaker_counts[q.speaker] += 1

            # Top speakers
            top_speakers = [
                {"name": name, "count": count}
                for name, count in speaker_counts.most_common(5)
            ]

            # Official dominance ratio
            official_count = role_counts.get("Government/Official", 0)
            official_ratio = round(official_count / total, 2) if total > 0 else 0.0

            stats_list.append(SpeakerBalanceStats(
                source=art.source,
                total_quotes=total,
                role_distribution=dict(role_counts),
                top_speakers=top_speakers,
                official_dominance_ratio=official_ratio
            ))

        return stats_list

quote_balance_analyzer = QuoteBalanceAnalyzer()
