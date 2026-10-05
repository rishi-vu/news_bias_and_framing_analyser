import re
from typing import List
from backend.app.models.schemas import Quote

class QuoteExtractor:
    def __init__(self):
        # Attribution speech verbs
        self.speech_verbs = (
            r'(?:said|declared|insisted|warned|stated|noted|argued|pointed out|emphasized|announced|told reporters)'
        )
        # Direct quote pattern: text inside quotes followed or preceded by speaker
        self.direct_quote_regex = re.compile(
            r'["“]([^"”]{10,400})["”]'
        )
        
        # Role inference keywords
        self.role_keywords = {
            "Government/Official": [
                "commissioner", "official", "trade ministry", "department", "spokesman",
                "spokesperson", "regulator", "chairman", "chairwoman", "parliament",
                "white house", "minister", "secretary", "senator", "governor",
                "president", "prime minister", "ambassador", "diplomat", "administration"
            ],
            "Expert/Academic": [
                "analyst", "director", "professor", "researcher", "economist",
                "scientist", "fellow", "expert", "watchdog", "institute", "think tank",
                "study", "report", "data", "survey", "university", "academic"
            ],
            "Industry/Corporate": [
                "coalition", "enterprise", "venture capital", "industry", "ceo",
                "business", "founders", "investors", "corporation", "company",
                "executive", "manager", "board", "shareholder", "startup", "firm"
            ],
            "Citizen/Activist": [
                "advocate", "activist", "workers", "communities", "families",
                "justice", "grassroots", "union", "resident", "voter", "protester",
                "campaigner", "volunteer", "citizen", "member of public"
            ]
        }

    def infer_role(self, speaker_context: str) -> str:
        speaker_lower = speaker_context.lower()
        for role, keywords in self.role_keywords.items():
            for kw in keywords:
                if kw in speaker_lower:
                    return role
        return "Unknown"  # Fixed: was 'Official/Spokesperson' which inflated official ratios

    def extract_quotes_from_sentences(self, sentences: List[str]) -> List[Quote]:
        quotes = []
        quote_counter = 0

        for idx, sent in enumerate(sentences):
            # Check for direct quote marks
            for match in self.direct_quote_regex.finditer(sent):
                quote_text = match.group(1).strip()
                # Find speaker in the surrounding sentence outside the quotes
                outside_text = sent.replace(match.group(0), "")
                
                # Check for attribution patterns: e.g. "declared Sophia Chen, policy director at..."
                speaker_match = re.search(
                    r'(?:' + self.speech_verbs + r')\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}(?:,\s+[^.]+)?)|([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}(?:,\s+[^.]+)?)\s+(?:' + self.speech_verbs + r')',
                    outside_text
                )
                
                speaker = "Reported Speaker"
                if speaker_match:
                    speaker = (speaker_match.group(1) or speaker_match.group(2) or "").strip()
                    # trim trailing punctuation
                    speaker = re.sub(r'[,.]+$', '', speaker)
                    if not speaker:
                        speaker = "Official Source"
                else:
                    # General speaker search
                    name_cand = re.search(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b', outside_text)
                    if name_cand:
                        speaker = name_cand.group(1)

                role = self.infer_role(speaker + " " + outside_text)

                quotes.append(Quote(
                    quote_id=f"quote_{quote_counter}",
                    quote_text=quote_text,
                    speaker=speaker,
                    speaker_role=role,
                    is_direct=True,
                    sentence_idx=idx
                ))
                quote_counter += 1

            # Check for indirect quotes if no direct quote was found
            if not quotes or quotes[-1].sentence_idx != idx:
                indirect_match = re.search(
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\s+(' + self.speech_verbs + r')\s+that\s+([^.]+)',
                    sent,
                    re.IGNORECASE
                )
                if indirect_match:
                    subj = indirect_match.group(1).strip()
                    content = indirect_match.group(3).strip()
                    if len(content.split()) >= 6:
                        quotes.append(Quote(
                            quote_id=f"quote_{quote_counter}",
                            quote_text=content,
                            speaker=subj if len(subj) > 2 else "Anonymous Source",
                            speaker_role=self.infer_role(subj + " " + sent),
                            is_direct=False,
                            sentence_idx=idx
                        ))
                        quote_counter += 1

        return quotes

quote_extractor = QuoteExtractor()
