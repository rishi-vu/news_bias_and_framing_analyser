from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional

from backend.app.config import settings
from backend.app.models.schemas import (
    ArticleInput, AnalysisRequest, ScrapeRequest,
    ArticleAnalysisResult, CrossSourceComparison,
    EvidenceQuery, RAGResponse
)
from backend.app.collection.scraper import scraper
from backend.app.collection.sample_datasets import (
    get_sample_events, get_sample_by_id, SAMPLE_STORIES
)
from backend.app.clustering.event_clustering import event_clusterer
from backend.app.retrieval.rag_engine import rag_engine
from backend.app.pipeline import pipeline

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Explainable Multi-Source News Bias and Framing Analyzer API"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get(f"{settings.API_PREFIX}/health")
def health_check():
    from backend.app.embeddings.embedder import embedder
    return {
        "status": "healthy",
        "embedder_ready": embedder.model is not None,
        "model_name": settings.EMBEDDING_MODEL_NAME
    }

@app.get(f"{settings.API_PREFIX}/sample-events")
def list_sample_events():
    """Retrieve pre-configured multi-source benchmark stories"""
    return get_sample_events()

@app.get(f"{settings.API_PREFIX}/sample-events/{{event_id}}")
def get_sample_event_detail(event_id: str):
    """Retrieve full articles for a specific benchmark story"""
    event = get_sample_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Sample event not found")
    return event

@app.post(f"{settings.API_PREFIX}/scrape")
def scrape_article_url(req: ScrapeRequest):
    """Scrape and clean article text from any live news URL"""
    try:
        article_data = scraper.scrape_url(req.url, req.source_name)
        return article_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")

@app.post(f"{settings.API_PREFIX}/cluster")
def cluster_articles_endpoint(articles: List[ArticleInput]):
    """Group incoming articles into semantic event clusters using sentence embeddings"""
    if not articles:
        raise HTTPException(status_code=400, detail="No articles provided for clustering")
    clusters = event_clusterer.cluster_articles(articles)
    return clusters

@app.post(f"{settings.API_PREFIX}/analyze")
def analyze_articles_endpoint(req: AnalysisRequest):
    """
    Run full end-to-end multi-source analysis pipeline:
    Preprocessing -> NLP Extraction (NER, Claims, Quotes) ->
    ML Analysis (Sentiment, Stance, Framing, Emotion, Loaded Language) ->
    Vector DB Indexing -> Cross-Source Engine -> Explainability & Bias Indicators
    """
    if not req.articles:
        raise HTTPException(status_code=400, detail="At least one article must be provided")

    topic = req.event_topic or (req.articles[0].title if req.articles else "News Event")
    analyzed_articles, cross_source = pipeline.analyze_event_cross_source(req.articles, topic)

    return {
        "articles": analyzed_articles,
        "cross_source": cross_source
    }

@app.post(f"{settings.API_PREFIX}/retrieve-evidence", response_model=RAGResponse)
def retrieve_evidence_endpoint(query_req: EvidenceQuery):
    """
    RAG semantic search across analyzed articles to retrieve supporting/contradicting
    evidence sentences for a specific claim or framing aspect
    """
    return rag_engine.retrieve_evidence(
        query=query_req.query,
        target_sources=query_req.target_sources
    )

from pathlib import Path
from fastapi.staticfiles import StaticFiles

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"  # adjust to your build folder

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

