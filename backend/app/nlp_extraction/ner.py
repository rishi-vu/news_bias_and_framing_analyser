import re
from typing import List, Dict
from collections import defaultdict
from backend.app.models.schemas import EntityMention

class NamedEntityRecognizer:
    def __init__(self):
        # Known multi-word organizations, agencies, and geopolitical entities
        self.known_orgs = {
            "United Nations", "UN", "OECD", "Silicon Valley", "European Union", "EU", 
            "Federal Reserve", "Wall Street", "Congress", "Parliament", "Supreme Court",
            "White House", "Algorithmic Justice Global", "Enterprise Innovation Coalition",
            "Clean Future Coalition", "Energy Security Foundation", "Trade Ministry",
            "Energy Department", "OECD", "Reuters", "The Guardian", "Fox Business",
            "Associated Press", "Bloomberg", "Google", "Microsoft", "OpenAI", "Meta"
        }
        
        self.known_gpe = {
            "Geneva", "United States", "US", "USA", "Beijing", "China", "Europe",
            "Washington", "London", "Brussels", "California", "Germany", "France",
            "Japan", "Taiwan", "Switzerland"
        }

        # Patterns for capitalized noun phrases and honorifics
        self.person_honorifics = r'\b(Mr|Mrs|Ms|Dr|Prof|Sen|Rep|Gov|Commissioner|Director|President|Chairman|Chairwoman|Secretary)\b'

        # Number / statistic entities
        self.number_pattern = re.compile(
            r'(\$\s*\d+(?:[,.]\d+)*\s*(?:billion|million|trillion|thousand)?'  # dollar amounts
            r'|\b\d+(?:[,.]\d+)?\s*%'                                          # percentages
            r'|\b\d+(?:[,.]\d+)?\s*(?:billion|million|trillion)\b'             # large numbers
            r'|\b\d{4}\b)',                                                     # years
            re.IGNORECASE
        )

    def extract_entities(self, sentences: List[str]) -> List[EntityMention]:
        entity_counts = defaultdict(lambda: {"count": 0, "label": "MISC"})
        
        for sent in sentences:
            # Check known entities
            for org in self.known_orgs:
                if org in sent:
                    entity_counts[org]["count"] += len(re.findall(r'\b' + re.escape(org) + r'\b', sent))
                    entity_counts[org]["label"] = "ORG"
                    
            for gpe in self.known_gpe:
                if gpe in sent:
                    entity_counts[gpe]["count"] += len(re.findall(r'\b' + re.escape(gpe) + r'\b', sent))
                    entity_counts[gpe]["label"] = "GPE"

            # Check for Person names with honorifics or Title patterns (e.g. "Sophia Chen", "Marcus Weber", "David Sterling")
            person_pattern = re.compile(
                r'(?:' + self.person_honorifics + r'\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})'
            )
            for match in person_pattern.finditer(sent):
                name = match.group(1)
                if not name:
                    continue
                # Filter out known orgs/gpe and sentence start words that aren't names
                if name not in self.known_orgs and name not in self.known_gpe:
                    # Common false positives
                    if name in {"Under The", "The Agreement", "While Western", "Global Leaders", "Human Rights", "Venture Capital", "Free Market"}:
                        continue
                    
                    # If preceded by attribution verbs or title or honorific, very likely a person
                    is_person = False
                    if match.group(0).startswith(("Mr", "Dr", "Prof", "Sen", "Gov", "President", "Commissioner", "Chairman")):
                        is_person = True
                    elif re.search(r'\b(said|insisted|warned|declared|stated|noted|argued|pointed out)\b', sent):
                        is_person = True
                    elif len(name.split()) == 2:
                        is_person = True
                        
                    if is_person:
                        entity_counts[name]["count"] += 1
                        entity_counts[name]["label"] = "PERSON"

            # Check for laws and treaties
            law_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Act|Accord|Treaty|Pact|Agreement|Bill))\b', sent)
            for law in law_matches:
                entity_counts[law]["count"] += 1
                entity_counts[law]["label"] = "LAW/TREATY"

            # Check for numbers / statistics
            for num_match in self.number_pattern.finditer(sent):
                num_text = num_match.group(0).strip()
                entity_counts[num_text]["count"] += 1
                entity_counts[num_text]["label"] = "NUMBER"

        results = []
        for text, meta in sorted(entity_counts.items(), key=lambda x: x[1]["count"], reverse=True):
            if meta["count"] > 0:
                results.append(EntityMention(
                    text=text,
                    label=meta["label"],
                    count=meta["count"]
                ))
        return results

ner_extractor = NamedEntityRecognizer()
