import re
from typing import List, Optional
from backend.app.models.schemas import Claim

class ClaimExtractor:
    def __init__(self):
        # Modals indicating policy/normative stance or consequences
        self.normative_modals = re.compile(
            r'\b(must|should|ought to|threatens to|will destroy|will paralyze|will trigger|will suffocate|will wipe out|is a critical|cannot support|indispensable)\b',
            re.IGNORECASE
        )
        # Causal & consequence predicates
        self.causal_predicates = re.compile(
            r'\b(results in|leads to|causes|exacerbates|destroys|cripples|paralyzes|safeguards|guarantees|eliminates|triggers|jeopardizes)\b',
            re.IGNORECASE
        )
        # Statistical & numerical claims
        self.stat_patterns = re.compile(
            r'(\$\d+(?:\.\d+)?\s*(?:billion|million|trillion)?|\b\d+(?:\.\d+)?%\b|\b\d+\s*(?:gigawatts|nations|jobs|percent|months|years)\b)',
            re.IGNORECASE
        )
        # Attribution clauses
        self.attribution_patterns = re.compile(
            r'(according to\s+[^,;]+|(?:warned|stated|argued|declared|insisted|pointed out|estimated)\s+that\s+[^,;.]+)',
            re.IGNORECASE
        )

    def extract_claims_from_sentences(self, sentences: List[str]) -> List[Claim]:
        claims = []
        for idx, sent in enumerate(sentences):
            is_claim = False
            claim_type = "factual"
            attribution = None

            # Check attribution
            attr_match = self.attribution_patterns.search(sent)
            if attr_match:
                attribution = attr_match.group(0).strip()

            # Check for statistical claim
            stat_match = self.stat_patterns.search(sent)
            if stat_match:
                is_claim = True
                claim_type = "statistic"

            # Check for normative / policy claim
            norm_match = self.normative_modals.search(sent)
            if norm_match:
                is_claim = True
                claim_type = "normative"

            # Check for causal assertion
            causal_match = self.causal_predicates.search(sent)
            if causal_match:
                is_claim = True
                if claim_type != "normative":
                    claim_type = "causal/factual"

            # Check if sentence has strong declarative structure with attribution
            if attribution and len(sent.split()) > 8:
                is_claim = True

            if is_claim:
                claims.append(Claim(
                    claim_id=f"claim_{idx}",
                    text=sent.strip(),
                    sentence_idx=idx,
                    claim_type=claim_type,
                    attribution=attribution,
                    confidence=0.88 if stat_match or norm_match else 0.76
                ))

        return claims

claim_extractor = ClaimExtractor()
