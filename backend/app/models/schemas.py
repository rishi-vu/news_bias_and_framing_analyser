from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# Input models
class ArticleInput(BaseModel):
    id: Optional[str] = None
    title: str
    source: str
    url: Optional[str] = ""
    content: str
    author: Optional[str] = ""
    published_date: Optional[str] = ""

class AnalysisRequest(BaseModel):
    articles: List[ArticleInput]
    event_topic: Optional[str] = None

class ScrapeRequest(BaseModel):
    url: str
    source_name: Optional[str] = None

# NLP & ML Layer Models
class EntityMention(BaseModel):
    text: str
    label: str  # PERSON, ORG, GPE, EVENT, LAW, MISC
    count: int = 1
    sentiment_context: Optional[float] = 0.0

class Claim(BaseModel):
    claim_id: str
    text: str
    sentence_idx: int
    claim_type: str  # factual, normative, policy, statistic
    attribution: Optional[str] = None
    confidence: float = 0.85

class Quote(BaseModel):
    quote_id: str
    quote_text: str
    speaker: str
    speaker_role: str  # Government/Official, Expert/Academic, Politician, Citizen/Victim, Unknown
    is_direct: bool = True
    sentence_idx: int

class LoadedSpan(BaseModel):
    term: str
    category: str  # sensationalism, subjective_qualifier, emotional_modifier, ideological_label
    start_char: int
    end_char: int
    severity: float  # 0.0 - 1.0

class SentenceAnalysis(BaseModel):
    sentence_idx: int
    text: str
    sentiment_score: float  # -1.0 to 1.0
    sentiment_label: str    # Positive, Neutral, Negative
    stance: str             # Support, Oppose, Neutral
    stance_score: float
    framing_scores: Dict[str, float]  # Economic, Conflict, Human Interest, Morality, Policy
    primary_frame: str
    emotion_scores: Dict[str, float]  # Anger, Fear, Joy, Sadness, Neutral
    primary_emotion: str
    loaded_spans: List[LoadedSpan] = []
    has_loaded_language: bool = False

# Article-Level Analysis
class ArticleAnalysisResult(BaseModel):
    article_id: str
    title: str
    source: str
    url: Optional[str] = ""
    sentence_count: int
    sentences: List[SentenceAnalysis]
    entities: List[EntityMention]
    claims: List[Claim]
    quotes: List[Quote]
    
    # Aggregates
    aggregate_sentiment: Dict[str, float]
    aggregate_framing: Dict[str, float]
    aggregate_emotions: Dict[str, float]
    aggregate_stance: Dict[str, float]
    loaded_language_density: float  # Loaded words per 100 sentences
    speaker_voice_diversity: float  # 0.0 - 1.0

# Cross-Source Models
class ClaimAlignment(BaseModel):
    claim_a: Claim
    source_a: str
    claim_b: Optional[Claim] = None
    source_b: Optional[str] = None
    similarity_score: float
    relation: str  # concordant, diverging, unsupported_in_b

class OmissionItem(BaseModel):
    aspect_key: str
    description: str
    reported_by: List[str]
    omitted_by: List[str]
    representative_sentence: str
    salience_score: float

class SpeakerBalanceStats(BaseModel):
    source: str
    total_quotes: int
    role_distribution: Dict[str, int]
    top_speakers: List[Dict[str, Any]]
    official_dominance_ratio: float

class BiasIndicator(BaseModel):
    indicator_type: str  # Framing Bias, Selective Omission, Loaded Language, Sourcing Imbalance, Tone Divergence
    severity: str        # High, Medium, Low
    confidence: float
    title: str
    explanation: str
    evidence_examples: List[Dict[str, Any]]

class CrossSourceComparison(BaseModel):
    event_title: str
    sources_analyzed: List[str]
    framing_divergence_matrix: Dict[str, Dict[str, float]]
    sentiment_divergence_matrix: Dict[str, Dict[str, float]]
    claim_comparisons: List[ClaimAlignment]
    omissions: List[OmissionItem]
    speaker_balance: List[SpeakerBalanceStats]
    bias_indicators: List[BiasIndicator]
    synthesis_summary: str

# RAG & Evidence Retrieval
class EvidenceQuery(BaseModel):
    query: str
    target_sources: Optional[List[str]] = None
    aspect_filter: Optional[str] = None

class EvidencePassage(BaseModel):
    source: str
    article_title: str
    sentence_text: str
    similarity_score: float
    framing: str
    sentiment: str
    loaded_terms: List[str]

class RAGResponse(BaseModel):
    query: str
    retrieved_evidence: List[EvidencePassage]
    contrastive_explanation: str
