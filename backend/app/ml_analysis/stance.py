from typing import Tuple, Dict

class StanceDetector:
    def __init__(self):
        self.support_cues = {
            "hailed", "breakthrough", "praised", "vital", "safeguard", "historic",
            "transformative", "indispensable", "visionary", "welcomed", "progress",
            "backed", "approved", "celebrated", "pledge", "advancing", "success"
        }
        self.oppose_cues = {
            "stifling", "power-grab", "suffocating", "paralyze", "disastrous",
            "catastrophic", "overreach", "crippling", "destroy", "wipe out",
            "burdensome", "onerous", "condemned", "jeopardizes", "threatens",
            "reckless", "ruin", "unproven", "taxpayer expense", "opposed"
        }
        self.neutral_cues = {
            "ratified", "established", "multilateral", "schedule", "protocols",
            "transition", "provisions", "inspections", "compromise", "framework",
            "estimated", "stated", "announced", "reported", "meeting", "treaty"
        }

    def detect_stance(self, sentence: str, sentiment_score: float) -> Tuple[str, float]:
        text_lower = sentence.lower()
        
        support_hits = sum(1 for cue in self.support_cues if cue in text_lower)
        oppose_hits = sum(1 for cue in self.oppose_cues if cue in text_lower)
        neutral_hits = sum(1 for cue in self.neutral_cues if cue in text_lower)

        # Balance with sentiment
        score = (support_hits * 0.4 + max(0.0, sentiment_score) * 0.6) - (oppose_hits * 0.4 + max(0.0, -sentiment_score) * 0.6)

        if score > 0.20 or support_hits > oppose_hits:
            confidence = min(0.95, 0.6 + support_hits * 0.15)
            return "Support", round(confidence, 2)
        elif score < -0.20 or oppose_hits > support_hits:
            confidence = min(0.95, 0.6 + oppose_hits * 0.15)
            return "Oppose", round(confidence, 2)
        else:
            confidence = min(0.95, 0.65 + neutral_hits * 0.1)
            return "Neutral", round(confidence, 2)

stance_detector = StanceDetector()
