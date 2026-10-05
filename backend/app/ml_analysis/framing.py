import re
from typing import Dict, Tuple

class FramingDetector:
    def __init__(self):
        self.frame_lexicons = {
            "Economic": {
                "keywords": [
                    "cost", "costs", "billion", "million", "dollar", "tax", "taxes",
                    "jobs", "inflation", "market", "markets", "competitiveness",
                    "investment", "investors", "expense", "budgets", "prices",
                    "venture capital", "startups", "enterprise", "financial",
                    "debt", "manufacturing", "economy", "trade", "subsidies"
                ],
                "weight": 1.0
            },
            "Conflict": {
                "keywords": [
                    "adversaries", "rivals", "power-grab", "strangle", "clash",
                    "battle", "partisan", "fight", "dominate", "opponents",
                    "overreach", "defiance", "struggle", "enemies", "showdown",
                    "dispute", "standoff", "compete", "hostile", "retaliate"
                ],
                "weight": 1.0
            },
            "Human Interest": {
                "keywords": [
                    "families", "children", "workers", "communities", "victims",
                    "suffering", "plight", "marginalized", "people", "individuals",
                    "patients", "lives", "unemployment", "hardship", "citizens",
                    "personal", "everyday", "grassroots", "asthma", "healthcare"
                ],
                "weight": 1.0
            },
            "Morality": {
                "keywords": [
                    "justice", "exploitative", "reckless", "impunity", "greed",
                    "predatory", "ethical", "ethics", "rights", "moral", "duty",
                    "discriminatory", "unconscionable", "integrity", "sinister",
                    "fairness", "pledge", "responsibility", "virtue", "evil"
                ],
                "weight": 1.0
            },
            "Policy & Law": {
                "keywords": [
                    "treaty", "accord", "act", "legislation", "mandates", "protocols",
                    "compliance", "statutory", "regulations", "oversight", "jurisdiction",
                    "ratified", "bipartisan", "committee", "provisions", "inspections",
                    "amendment", "lawmakers", "parliament", "framework", "standards"
                ],
                "weight": 1.0
            }
        }

    def detect_framing(self, sentence: str) -> Tuple[Dict[str, float], str]:
        text_lower = sentence.lower()
        scores = {}
        total = 0.0

        for frame_name, frame_data in self.frame_lexicons.items():
            hits = 0
            for kw in frame_data["keywords"]:
                # Match whole words or phrases
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    hits += 1
            score = hits * frame_data["weight"]
            scores[frame_name] = score
            total += score

        # Normalize to probability distribution
        if total > 0:
            norm_scores = {k: round(v / total, 3) for k, v in scores.items()}
            primary = max(norm_scores.items(), key=lambda x: x[1])[0]
        else:
            norm_scores = {k: 0.20 for k in self.frame_lexicons.keys()}
            primary = "Policy & Law"  # standard baseline for news

        return norm_scores, primary

framing_detector = FramingDetector()
