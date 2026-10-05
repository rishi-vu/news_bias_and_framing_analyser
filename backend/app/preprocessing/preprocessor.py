import re
import html
import unicodedata
from typing import List
import nltk

try:
    from nltk.tokenize import sent_tokenize
except Exception:
    sent_tokenize = None

class DataPreprocessor:
    def __init__(self):
        # Common abbreviations to prevent false sentence breaks
        self.abbrev_pattern = re.compile(
            r'\b(Mr|Mrs|Ms|Dr|Prof|Sen|Rep|Gov|Gen|Col|Lt|St|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec|U\.S|U\.K|U\.N|E\.U|Corp|Inc|Ltd|Co|approx|al)\.',
            re.IGNORECASE
        )

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Unescape HTML entities
        text = html.unescape(text)
        # Normalize unicode (e.g. smart quotes, dashes)
        text = unicodedata.normalize("NFKC", text)
        # Standardize quotes and hyphens
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        text = text.replace("—", " - ").replace("–", " - ")
        # Strip consecutive whitespaces and excessive line breaks
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()

    def segment_sentences(self, text: str) -> List[str]:
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        # Use NLTK punkt if available
        if sent_tokenize:
            try:
                # Protect abbreviations with temporary placeholder
                protected = self.abbrev_pattern.sub(lambda m: m.group(0).replace(".", "@@DOT@@"), cleaned)
                raw_sentences = sent_tokenize(protected)
                sentences = [s.replace("@@DOT@@", ".").strip() for s in raw_sentences]
            except Exception:
                sentences = self._fallback_sent_tokenize(cleaned)
        else:
            sentences = self._fallback_sent_tokenize(cleaned)

        # Refine sentences: filter out tiny fragments, clean quotes
        refined = []
        for s in sentences:
            s_clean = s.strip()
            # Ignore sentences that are just lone numbers, punctuation, or fewer than 3 words
            if len(s_clean.split()) >= 3:
                refined.append(s_clean)
        
        return self.deduplicate_sentences(refined)

    def _fallback_sent_tokenize(self, text: str) -> List[str]:
        # Regex split on period, exclamation, question mark followed by space and uppercase or quote
        pattern = r'(?<=[.!?])\s+(?=[A-Z"\'“])'
        parts = re.split(pattern, text)
        return [p.strip() for p in parts if p.strip()]

    def deduplicate_sentences(self, sentences: List[str]) -> List[str]:
        seen = set()
        unique = []
        for s in sentences:
            # normalized form for comparison
            normalized = re.sub(r'[^a-zA-Z0-9]', '', s.lower())
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique.append(s)
        return unique

preprocessor = DataPreprocessor()
