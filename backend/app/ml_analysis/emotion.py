import re
from typing import Dict, Tuple

class EmotionDetector:
    def __init__(self):
        self.emotion_lexicons = {
            "Anger": [
                "power-grab", "rammed through", "strangle", "suffocating", "paralyze",
                "outrage", "furious", "reckless", "impunity", "predatory", "crushing",
                "punitive", "heavy-handed", "arrogant", "corrupt"
            ],
            "Fear": [
                "threatens", "jeopardizes", "catastrophic", "collapse", "blackouts",
                "alarm", "ruin", "crisis", "disastrous", "danger", "peril", "vulnerable",
                "casualties", "casualty", "looming", "grim"
            ],
            "Joy / Optimism": [
                "hailed", "breakthrough", "celebrated", "historic", "visionary",
                "triumph", "transformative", "vibrant", "prosperity", "pledge",
                "success", "welcomed", "promising", "delighted"
            ],
            "Sadness / Empathy": [
                "suffering", "plight", "unemployment", "hardship", "loss", "grief",
                "abandonment", "beleaguered", "contaminated", "struggling", "hurt"
            ],
            "Neutral": [
                "ratified", "established", "announced", "protocol", "meeting",
                "schedule", "data", "report", "percent", "standard", "provision"
            ]
        }

    def detect_emotion(self, sentence: str) -> Tuple[Dict[str, float], str]:
        text_lower = sentence.lower()
        counts = {}
        total = 0

        for emotion, keywords in self.emotion_lexicons.items():
            hit_count = 0
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    hit_count += 1
            counts[emotion] = hit_count
            total += hit_count

        if total > 0:
            norm_scores = {k: round(v / total, 3) for k, v in counts.items()}
            # Exclude neutral if an intense emotion was detected
            emotional_subset = {k: v for k, v in norm_scores.items() if k != "Neutral" and v > 0}
            if emotional_subset:
                primary = max(emotional_subset.items(), key=lambda x: x[1])[0]
            else:
                primary = "Neutral"
        else:
            norm_scores = {
                "Anger": 0.05,
                "Fear": 0.05,
                "Joy / Optimism": 0.05,
                "Sadness / Empathy": 0.05,
                "Neutral": 0.80
            }
            primary = "Neutral"

        return norm_scores, primary

emotion_detector = EmotionDetector()
