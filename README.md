# Explainable Multi-Source News Bias and Framing Analyzer

A state-of-the-art NLP and Machine Learning system that systematically detects, analyzes, and explains **linguistic framing**, **selective reporting (omissions)**, **source imbalance**, and **stance differences** across multiple news outlets covering the same event.

Instead of relying on a single opaque black-box label, the system combines transformer embeddings, semantic similarity, clustering, cross-document analysis, and evidence retrieval to produce **evidence-backed bias indicators with calibrated confidence scores and highlighted text explanations**.

---

## 🏛️ System Architecture Alignment

The system maps directly 1-to-1 to each layer of the specified architecture:

```text
                    NEWS SOURCES
                         │
                         ▼
                Article Collection          ───► backend/app/collection/
             Scraping / News APIs / URLs           • scraper.py (HTML & meta extractor)
                         │                         • sample_datasets.py (multi-source benchmarks)
                         ▼
                 Data Preprocessing         ───► backend/app/preprocessing/
          Cleaning • Sentence Segmentation         • preprocessor.py (NLTK punkt, abbrev guard,
          Deduplication • Normalization              deduplication, unicode cleanup)
                         │
                         ▼
                NLP EXTRACTION LAYER        ───► backend/app/nlp_extraction/
        ┌────────────────┼─────────────────┐       • ner.py (PERSON, ORG, GPE, LAW/TREATY)
        ▼                ▼                 ▼       • claim_extractor.py (Factual, Normative, Stat)
      Named            Claim            Quote /    • quote_extractor.py (Direct quotes, attributions,
      Entity          Extraction        Speaker      speaker role classification)
    Recognition                         Extraction
        │                │                 │
        └────────────────┼─────────────────┘
                         ▼
                 ML ANALYSIS LAYER          ───► backend/app/ml_analysis/
      ┌──────────┬───────┼────────┬───────────┐    • sentiment.py (Contextual polarity & intensity)
      ▼          ▼       ▼        ▼           ▼    • stance.py (Support, Oppose, Neutral)
 Sentiment    Stance   Framing   Emotion    Loaded • framing.py (Media Frames Corpus dimensions:
 Analysis    Detection Detection Detection   Lang    Economic, Conflict, Human Interest, Morality, Policy)
      │          │       │        │           │    • emotion.py (Anger, Fear, Joy, Sadness, Neutral)
      └──────────┴───────┼────────┴───────────┘    • loaded_language.py (Sensationalism, hyperbole,
                         ▼                           pejoratives with exact character offsets)
              Transformer Embeddings        ───► backend/app/embeddings/
              Sentence-Transformer                 • embedder.py (all-MiniLM-L6-v2 384d vectors)
                         │
                         ▼
                   VECTOR DATABASE          ───► backend/app/vector_db/
                FAISS / Qdrant / Chroma            • vector_store.py (Cosine similarity normalized index)
                         │
                         ▼
                   EVENT CLUSTERING         ───► backend/app/clustering/
              HDBSCAN / Agglomerative              • event_clustering.py (Agglomerative cosine clustering)
                         │
                         ▼
               CROSS-SOURCE ENGINE          ───► backend/app/cross_source/
          ┌──────────────┼──────────────┐          • claim_comparison.py (Concordant vs Diverging)
          ▼              ▼              ▼          • omission_detection.py (Selective reporting matrix)
       Claim          Coverage        Source /     • quote_balance.py (Voice diversity & authority ratio)
     Comparison       Omission         Quote
                      Detection        Balance
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                EVIDENCE RETRIEVAL          ───► backend/app/retrieval/
                         │                         • rag_engine.py (Dense vector passage search &
                         ▼                           contrastive cross-source synthesis)
                       RAG
                Retrieved Evidence
                       + LLM
                         │
                         ▼
              EXPLAINABILITY ENGINE         ───► backend/app/explainability/
             Bias Indicators + Evidence            • explainer.py (Calibrated confidence scores,
             Confidence + Highlighted Text           framing divide, tone shift, natural language)
                         │
                         ▼
                    FastAPI API             ───► backend/app/main.py
                         │                         • REST Endpoints (/analyze, /scrape, /cluster,
                         ▼                           /retrieve-evidence, /sample-events)
                 ANALYTICS DASHBOARD        ───► frontend/
              React / Next.js / Plotly             • Side-by-side reading room with interactive highlights
                                                   • MFC Framing radar & stance comparison
                                                   • Coverage omission matrix
                                                   • Claim concordance matrix
                                                   • Voice diversity & quoted speaker breakdown
                                                   • Live Semantic Evidence RAG search
```

---

## 🚀 Quick Start Guide

### 1. Launch Everything with One Command
```bash
./run.sh
```
* **FastAPI Backend & API Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)
* **Interactive Analytics Dashboard**: [http://localhost:5173](http://localhost:5173)

---

## 🔍 Core Features Demonstrated

1. **Side-by-Side Reading Room with Interactive Span Highlighting**:
   - 🔴 **Loaded Language**: Sensationalist metaphors (`"suffocating"`, `"power-grab"`, `"predatory"`) with severity scores and explanatory tooltips.
   - 🔵 **Claims & Numbers**: Highlights declarative propositions, statistics (`$48 billion`, `1.4%`), and normative statements.
   - 🟣 **Quotes & Speakers**: Direct & indirect quotations attributed to speakers with role tags (*Government/Official*, *Expert/Academic*, *Citizen/Activist*, *Industry/Executive*).

2. **Media Frames Corpus (MFC) Multi-Source Breakdown**:
   - Quantitative evaluation across 5 canonical dimensions: *Economic Consequences*, *Conflict & Strategy*, *Human Interest*, *Morality & Ethics*, and *Policy & Law*.

3. **Selective Reporting & Coverage Omission Matrix**:
   - Detects facts or context reported by Outlet A that Outlet B or C completely excluded, computing a salience score and presenting the representative evidence sentence.

4. **Claim Concordance & Divergence**:
   - Aligns claims addressing the same event sub-topics and highlights whether the outlets agree (*concordant*), present conflicting evaluations (*diverging*), or assert points uncorroborated elsewhere (*unsupported*).

5. **Speaker & Quoted Voice Diversity**:
   - Quantifies authority dominance vs civilian voice representation to expose single-source dependency.

6. **Semantic Evidence RAG Engine**:
   - Search across all multi-source sentences using dense vector embeddings to compare how opposing outlets addressed specific questions or facts.
