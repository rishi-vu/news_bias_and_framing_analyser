import re
from typing import Tuple, Dict

class SentimentAnalyzer:
    def __init__(self):
        # Lexicon for contextual sentiment polarity and intensity
        self.pos_words = {
            # Strong positive
            "breakthrough": 0.85, "historic": 0.65, "safeguard": 0.75, "praised": 0.70,
            "protection": 0.60, "vibrant": 0.70, "prosperity": 0.80, "visionary": 0.80,
            "indispensable": 0.70, "progress": 0.65, "success": 0.75, "robust": 0.65,
            "solution": 0.55, "benefit": 0.65, "opportunity": 0.65, "promising": 0.65,
            "safeguards": 0.70, "transformative": 0.80, "triumph": 0.90, "positive": 0.60,
            "harmony": 0.70, "innovative": 0.65, "collaborative": 0.55, "balance": 0.45,
            # Extended
            "groundbreaking": 0.85, "landmark": 0.75, "pivotal": 0.65, "vital": 0.60,
            "praised": 0.70, "welcomed": 0.65, "celebrated": 0.75, "commended": 0.70,
            "endorsed": 0.65, "supported": 0.55, "secured": 0.60, "achieved": 0.65,
            "strengthens": 0.65, "boosts": 0.60, "bolsters": 0.65, "empowers": 0.70,
            "milestone": 0.75, "agreement": 0.45, "cooperation": 0.55, "constructive": 0.55,
            "effective": 0.55, "significant": 0.40, "crucial": 0.45, "essential": 0.50,
            "unprecedented": 0.55, "sweeping": 0.50, "bold": 0.60, "comprehensive": 0.50,
        }
        self.neg_words = {
            # Strong negative
            "exploitative": -0.80, "reckless": -0.80, "casualty": -0.70,
            "predatory": -0.85, "impunity": -0.75, "discriminatory": -0.80,
            "threatens": -0.65, "stifling": -0.75, "crippling": -0.85,
            "power-grab": -0.90, "suffocating": -0.80, "paralyze": -0.80,
            "crushing": -0.80, "disastrous": -0.90, "catastrophic": -0.90,
            "destroy": -0.80, "onerous": -0.70, "radical": -0.60,
            "collapse": -0.80, "jeopardizes": -0.75, "ruin": -0.80,
            "toxic": -0.75, "controversial": -0.40, "crisis": -0.70, "danger": -0.65,
            # Extended
            "alarming": -0.75, "concerning": -0.55, "troubling": -0.65, "worrying": -0.60,
            "failed": -0.75, "failure": -0.75, "flawed": -0.65, "inadequate": -0.60,
            "harmful": -0.75, "damaging": -0.70, "detrimental": -0.70, "devastating": -0.85,
            "slammed": -0.80, "blasted": -0.75, "condemned": -0.80, "rejected": -0.65,
            "opposed": -0.55, "criticized": -0.60, "disputed": -0.55, "contested": -0.50,
            "turbulent": -0.60, "fragile": -0.55, "volatile": -0.65, "unstable": -0.65,
            "burden": -0.55, "costly": -0.55, "excessive": -0.60, "extreme": -0.55,
            "risk": -0.45, "threat": -0.65, "attack": -0.70, "scandal": -0.80,
            "corrupt": -0.85, "fraud": -0.85, "illegal": -0.80, "violation": -0.75,
            "shocking": -0.70, "outrageous": -0.80, "bombshell": -0.70, "explosive": -0.65,
            "whitewash": -0.75, "coverup": -0.80, "incompetent": -0.80,
        }
        self.intensifiers = {
            "very": 1.3, "extremely": 1.5, "severely": 1.5, "relentless": 1.4,
            "deeply": 1.3, "wholly": 1.2, "massive": 1.4, "completely": 1.3
        }
        self.diminishers = {
            "somewhat": 0.7, "slightly": 0.6, "partially": 0.7, "barely": 0.4
        }
        self.negations = {
            "not", "never", "no", "without", "neither", "hardly", "scarcely"
        }

    def analyze_sentence(self, sentence: str) -> Tuple[float, str]:
        words = re.findall(r'\b[a-zA-Z\-]+\b', sentence.lower())
        if not words:
            return 0.0, "Neutral"

        score = 0.0
        multiplier = 1.0
        is_negated = False
        matched_count = 0

        for idx, word in enumerate(words):
            if word in self.negations:
                is_negated = True
                continue

            current_weight = 1.0
            # Check previous word for intensifiers/diminishers
            if idx > 0:
                prev_word = words[idx - 1]
                if prev_word in self.intensifiers:
                    current_weight = self.intensifiers[prev_word]
                elif prev_word in self.diminishers:
                    current_weight = self.diminishers[prev_word]

            if word in self.pos_words:
                val = self.pos_words[word] * current_weight
                score += -val if is_negated else val
                matched_count += 1
                is_negated = False
            elif word in self.neg_words:
                val = self.neg_words[word] * current_weight
                score += -val if is_negated else val
                matched_count += 1
                is_negated = False

        if matched_count == 0:
            final_score = 0.0
        else:
            # Bound score between -1.0 and 1.0
            final_score = max(-1.0, min(1.0, score / max(1.0, matched_count ** 0.5)))

        if final_score > 0.15:
            label = "Positive"
        elif final_score < -0.15:
            label = "Negative"
        else:
            label = "Neutral"

        return round(final_score, 3), label

sentiment_analyzer = SentimentAnalyzer()
