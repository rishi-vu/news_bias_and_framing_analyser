import re
from typing import List, Tuple
from backend.app.models.schemas import LoadedSpan

class LoadedLanguageDetector:
    def __init__(self):
        # Dictionary mapping loaded phrases/words to category, severity, and explanation
        self.lexicon = {
            "power-grab": ("Sensationalism", 0.95, "Inflammatory political metaphor implying illegitimate usurpation of authority"),
            "unelected globalists": ("Ideological Pejorative", 0.90, "Populist partisan framing intended to delegitimize international delegates"),
            "suffocating": ("Sensationalism", 0.85, "Violent bodily metaphor used to depict economic regulation"),
            "paralyze": ("Sensationalism", 0.80, "Hyperbolic medical metaphor implying complete incapacitation"),
            "crippling": ("Sensationalism", 0.85, "Hyperbolic physical disability metaphor to describe economic costs"),
            "disastrous": ("Hyperbolic Qualifier", 0.85, "Extreme catastrophic assertion lacking empirical qualification"),
            "catastrophic": ("Hyperbolic Qualifier", 0.90, "Maximally loaded apocalyptic term"),
            "heavy-handed": ("Subjective Framing", 0.75, "Editorialized framing depicting governance as abusive"),
            "strangle": ("Sensationalism", 0.85, "Violent physical metaphor applied to business activities"),
            "predatory": ("Affective Pejorative", 0.85, "Accusatory framing attributing malicious predatory intent to corporations"),
            "exploitative": ("Ideological Framing", 0.80, "Normative political judgment presenting commercial activity as exploitation"),
            "reckless": ("Subjective Evaluation", 0.80, "Editorial judgment asserting dangerous disregard for consequences"),
            "corporate impunity": ("Ideological Rhetoric", 0.85, "Loaded phrase asserting intentional evasion of justice"),
            "billionaires": ("Ideological Target", 0.65, "Class-based emotional target framing"),
            "casualty": ("Sensationalism", 0.75, "Warfare/casualty metaphor applied to civic issues"),
            "rammed through": ("Sensationalism", 0.85, "Violent kinetic metaphor used to delegitimize legislative process"),
            "radical": ("Ideological Pejorative", 0.80, "Partisan framing delegitimizing political opposition as extremist"),
            "fantasy": ("Dismissive Pejorative", 0.75, "Editorial dismissal framing alternative policy as delusional"),
            "soaring": ("Sensationalism", 0.70, "Emotive amplifier to dramatize price or rate increases"),
            "sky-high": ("Sensationalism", 0.70, "Hyperbolic amplifier describing costs"),
            "devastating": ("Hyperbolic Qualifier", 0.85, "Maximal negative impact descriptor"),
            "visionary": ("Affective Praise", 0.75, "Uncritical laudatory descriptor celebrating policy"),
            "historic breakthrough": ("Affective Praise", 0.80, "Monumentalizing framing portraying agreement as epochal triumph"),
            "transformative": ("Affective Praise", 0.70, "Positive framing presupposing beneficial societal change"),
            "beleaguered": ("Emotive Framing", 0.75, "Victimhood framing emphasizing helplessness"),
            "red tape": ("Ideological Cliché", 0.70, "Partisan cliché designed to disparage administrative compliance"),
            "onerous": ("Subjective Evaluation", 0.70, "Evaluative adjective framing requirements as unduly burdensome"),
            "jeopardizes": ("Sensationalism", 0.75, "Alarmist verb predicting severe vulnerability"),
            "draconian": ("Hyperbolic Pejorative", 0.90, "Extreme pejorative comparing statutory policy to ancient tyranny")
        }

    def detect_loaded_spans(self, sentence: str) -> List[LoadedSpan]:
        spans = []
        sentence_lower = sentence.lower()

        for phrase, (category, severity, explanation) in self.lexicon.items():
            pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(sentence):
                spans.append(LoadedSpan(
                    term=match.group(0),
                    category=category,
                    start_char=match.start(),
                    end_char=match.end(),
                    severity=severity
                ))

        # Sort spans by starting position
        spans.sort(key=lambda s: s.start_char)
        return spans

loaded_language_detector = LoadedLanguageDetector()
