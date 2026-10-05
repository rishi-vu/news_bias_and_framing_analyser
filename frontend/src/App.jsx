import React, { useState, useEffect } from 'react';

const API_BASE = "http://localhost:8001/api";

const FRAME_INFO = [
  { name: "Economic",     desc: "Financial costs, trade, jobs, and markets." },
  { name: "Conflict",     desc: "Power struggles, rivalry, and political opposition." },
  { name: "Human Interest", desc: "Direct impact on everyday citizens and families." },
  { name: "Morality",     desc: "Ethics, justice, corporate responsibility." },
  { name: "Policy & Law", desc: "Legislation, regulations, compliance, treaties." },
];

const BAR_COLORS = ["#2563eb", "#7c3aed", "#d97706"];

export default function App() {
  const [sampleEvents, setSampleEvents] = useState([]);
  const [activeId, setActiveId]         = useState(
    () => localStorage.getItem('nl_activeId') || ""
  );
  const [loading, setLoading]           = useState(false);
  const [articles, setArticles]         = useState([]);
  const [crossSource, setCrossSource]   = useState(null);
  const [activeTab, setActiveTab]       = useState(
    () => localStorage.getItem('nl_tab') || "reading"
  );

  // Saved comparisons history — newest first
  const [savedComparisons, setSavedComparisons] = useState(
    () => { try { return JSON.parse(localStorage.getItem('nl_comparisons')) || []; } catch { return []; } }
  );

  const [hlLoaded, setHlLoaded] = useState(true);
  const [hlClaims, setHlClaims] = useState(true);
  const [hlQuotes, setHlQuotes] = useState(true);

  const [searchQuery, setSearchQuery]     = useState("");
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResult, setSearchResult]   = useState(null);

  const [showModal, setShowModal]           = useState(false);
  const [customArticles, setCustomArticles] = useState([
    { title: "", source: "Outlet A", content: "", url: "" },
    { title: "", source: "Outlet B", content: "", url: "" }
  ]);
  const [scrapeUrl, setScrapeUrl] = useState("");
  const [scraping, setScraping]   = useState(false);

  // Restore active comparison on mount
  useEffect(() => {
    const id = localStorage.getItem('nl_activeId');
    if (id) {
      const all = JSON.parse(localStorage.getItem('nl_comparisons') || '[]');
      const found = all.find(c => c.id === id);
      if (found) { setArticles(found.articles); setCrossSource(found.crossSource); }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('nl_tab', activeTab);
  }, [activeTab]);

  useEffect(() => {
    localStorage.setItem('nl_comparisons', JSON.stringify(savedComparisons));
  }, [savedComparisons]);

  useEffect(() => { fetchSamples(); }, []);

  const fetchSamples = async () => {
    try {
      const res = await fetch(`${API_BASE}/sample-events`);
      if (res.ok) {
        const data = await res.json();
        setSampleEvents(data);
        // Auto-load first sample only if nothing is saved yet
        const hasSaved = localStorage.getItem('nl_activeId');
        if (data.length > 0 && !hasSaved) {
          loadSampleEvent(data[0].id);
        }
      }
    } catch (err) { console.error(err); }
  };

  // Load a sample story — fetches & analyzes, saves result
  const loadSampleEvent = async (id) => {
    setActiveId(id);
    localStorage.setItem('nl_activeId', id);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/sample-events/${id}`);
      if (res.ok) {
        const data = await res.json();
        await analyzeAndSave(data.articles, data.title, id);
      }
    } catch (err) { console.error(err); setLoading(false); }
  };

  // Instantly restore a saved comparison by id
  const restoreComparison = (id) => {
    const found = savedComparisons.find(c => c.id === id);
    if (!found) return;
    setActiveId(id);
    localStorage.setItem('nl_activeId', id);
    setArticles(found.articles);
    setCrossSource(found.crossSource);
    setActiveTab('reading');
  };

  // Analyze articles and save the result into savedComparisons history
  const analyzeAndSave = async (arts, topic, id) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ articles: arts, event_topic: topic })
      });
      if (res.ok) {
        const data = await res.json();
        setArticles(data.articles);
        setCrossSource(data.cross_source);
        // Upsert into savedComparisons (newest first)
        setSavedComparisons(prev => {
          const filtered = prev.filter(c => c.id !== id);
          return [{ id, title: topic, articles: data.articles, crossSource: data.cross_source, isCustom: !id.startsWith('sample_') }, ...filtered];
        });
      }
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    try {
      const res = await fetch(`${API_BASE}/retrieve-evidence`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery })
      });
      if (res.ok) setSearchResult(await res.json());
    } catch (err) { console.error(err); }
    finally { setSearchLoading(false); }
  };

  const handleScrape = async () => {
    if (!scrapeUrl.trim()) return;
    setScraping(true);
    try {
      const res = await fetch(`${API_BASE}/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: scrapeUrl })
      });
      if (res.ok) {
        const data = await res.json();
        setCustomArticles([...customArticles, { title: data.title, source: data.source, content: data.content, url: data.url }]);
        setScrapeUrl("");
      }
    } catch { alert("Could not scrape URL. Please paste the text directly."); }
    finally { setScraping(false); }
  };

  const handleCustomSubmit = () => {
    const valid = customArticles.filter(a => a.title.trim() && a.content.trim());
    if (valid.length < 2) { alert("Please fill in at least 2 articles."); return; }
    setShowModal(false);
    // Generate unique id for this custom comparison
    const id = `custom_${Date.now()}`;
    const sources = valid.map(a => a.source).join(' vs ');
    const title = sources || 'Custom Comparison';
    setActiveId(id);
    localStorage.setItem('nl_activeId', id);
    analyzeAndSave(valid, title, id);
    // Reset modal form for next time
    setCustomArticles([
      { title: "", source: "Outlet A", content: "", url: "" },
      { title: "", source: "Outlet B", content: "", url: "" }
    ]);
  };

  const renderSentence = (sent) => {
    if (hlLoaded && sent.loaded_spans?.length > 0) {
      const parts = [];
      let last = 0;
      sent.loaded_spans.forEach((span, i) => {
        if (span.start_char > last) parts.push(sent.text.substring(last, span.start_char));
        parts.push(
          <span key={i} className="hl-emotional" title={span.category}>{span.term}</span>
        );
        last = span.end_char;
      });
      if (last < sent.text.length) parts.push(sent.text.substring(last));
      return parts;
    }
    return sent.text;
  };

  const deleteComparison = (id, e) => {
    e.stopPropagation();
    setSavedComparisons(prev => prev.filter(c => c.id !== id));
    if (activeId === id) {
      setArticles([]);
      setCrossSource(null);
      setActiveId("");
      localStorage.removeItem('nl_activeId');
    }
  };

  const TABS = [
    { id: "reading",   label: "Side by Side" },
    { id: "framing",   label: "Framing" },
    { id: "sentiment", label: "Sentiment" },
    { id: "claims",    label: `Claims${crossSource ? ` (${crossSource.claim_comparisons?.length || 0})` : ""}` },
    { id: "omissions", label: `Omissions${crossSource ? ` (${crossSource.omissions?.length || 0})` : ""}` },
    { id: "sourcing",  label: "Voices" },
    { id: "entities",  label: "Entities" },
    { id: "search",    label: "Search" },
  ];

  return (
    <div>
      {/* Header */}
      <header className="nav">
        <div className="nav-inner">
          <div className="wordmark">
            NewsLens
            <span className="wordmark-dot" />
            <span className="wordmark-sub">Multi-source bias & framing analyzer</span>
          </div>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button className="btn btn-ghost" onClick={() => setShowModal(true)}>
              Add Articles
            </button>
            <button
              className="btn btn-primary"
              onClick={() => {
                const found = savedComparisons.find(c => c.id === activeId);
                if (found) analyzeAndSave(found.articles.map(a => ({ title: a.title, source: a.source, content: a.sentences?.map(s=>s.text).join(' ') || '' })), found.title, activeId);
              }}
              disabled={loading}
            >
              {loading ? "Analyzing…" : "Re-analyze"}
            </button>
          </div>
        </div>
      </header>

      <main className="page">

        {/* Story Selector — custom comparisons first, then samples */}
        <div className="story-bar">
          <span className="story-bar-label">Compare:</span>

          {/* Custom comparisons (newest first) */}
          {savedComparisons.filter(c => c.isCustom).map(c => (
            <span key={c.id} style={{ display: 'inline-flex', alignItems: 'center', gap: 0 }}>
              <button
                className={`story-pill story-pill-custom${activeId === c.id ? " active" : ""}`}
                style={{ borderRadius: '20px 0 0 20px', borderRight: 'none' }}
                onClick={() => restoreComparison(c.id)}
                title={c.title}
              >
                {c.title.length > 28 ? c.title.slice(0, 26) + '…' : c.title}
              </button>
              <button
                className="story-pill-delete"
                onClick={(e) => deleteComparison(c.id, e)}
                title="Remove this comparison"
              >×</button>
            </span>
          ))}

          {/* Divider if both exist */}
          {savedComparisons.some(c => c.isCustom) && sampleEvents.length > 0 && (
            <span className="story-bar-divider" />
          )}

          {/* Sample stories */}
          {sampleEvents.map(evt => (
            <button
              key={evt.id}
              className={`story-pill${activeId === evt.id ? " active" : ""}`}
              onClick={() => {
                const saved = savedComparisons.find(c => c.id === evt.id);
                if (saved) restoreComparison(evt.id);
                else loadSampleEvent(evt.id);
              }}
            >
              {evt.title}
            </button>
          ))}
        </div>

        {/* Loading */}
        {loading && (
          <div className="loading-screen">
            <div className="loading-spinner" />
            <p className="loading-text">Analyzing articles across sources…</p>
          </div>
        )}

        {/* Summary Card */}
        {!loading && crossSource && (
          <div className="summary-card">
            <h1 className="summary-title">{crossSource.event_title}</h1>
            <p className="summary-body">{crossSource.synthesis_summary}</p>
            <div className="outlets-row">
              <span style={{ fontSize: "0.72rem", color: "var(--text-faint)" }}>Comparing:</span>
              {crossSource.sources_analyzed.map((src, i) => (
                <span key={i} className="outlet-tag">{src}</span>
              ))}
            </div>

            {crossSource.bias_indicators?.length > 0 && (
              <div className="indicators-row">
                {crossSource.bias_indicators.slice(0, 3).map((ind, i) => (
                  <div key={i} className="indicator-card">
                    <div className="indicator-type">
                      {ind.indicator_type}
                      <span className={`conf-badge ${ind.severity === "High" ? "conf-high" : ind.severity === "Medium" ? "conf-medium" : "conf-low"}`}>
                        {Math.round(ind.confidence * 100)}%
                      </span>
                    </div>
                    <div className="indicator-title">{ind.title}</div>
                    <div className="indicator-desc">{ind.explanation}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab Bar */}
        {!loading && crossSource && (
          <div className="tabs-bar">
            <div className="tabs">
              {TABS.map(t => (
                <button
                  key={t.id}
                  className={`tab${activeTab === t.id ? " active" : ""}`}
                  onClick={() => setActiveTab(t.id)}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {activeTab === "reading" && (
              <div className="hl-toggles">
                <span className="hl-label">Highlight:</span>
                <button
                  className={`hl-toggle${hlLoaded ? " on-red" : ""}`}
                  onClick={() => setHlLoaded(!hlLoaded)}
                >
                  Emotional words
                </button>
                <button
                  className={`hl-toggle${hlClaims ? " on-blue" : ""}`}
                  onClick={() => setHlClaims(!hlClaims)}
                >
                  Claims
                </button>
                <button
                  className={`hl-toggle${hlQuotes ? " on-purple" : ""}`}
                  onClick={() => setHlQuotes(!hlQuotes)}
                >
                  Quotes
                </button>
              </div>
            )}
          </div>
        )}

        {/* ── TAB: SIDE-BY-SIDE ── */}
        {!loading && activeTab === "reading" && articles.length > 0 && (
          <div
            className="reader-grid"
          >
            {articles.map((art, idx) => {
              const topFrame = Object.entries(art.aggregate_framing).sort((a, b) => b[1] - a[1])[0];
              const sentPol = art.aggregate_sentiment?.polarity ?? 0;
              const sentLabel = sentPol > 0.1 ? 'Positive' : sentPol < -0.1 ? 'Negative' : 'Neutral';
              const sentColor = sentPol > 0.1 ? 'var(--green)' : sentPol < -0.1 ? 'var(--red)' : 'var(--text-faint)';
              return (
                <div key={idx} className="article-card">
                  <div className="article-header">
                    <div className="article-source">{art.source}</div>
                    <div className="article-title">{art.title}</div>
                    <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.4rem', flexWrap: 'wrap' }}>
                      <span className="frame-pill">{topFrame ? topFrame[0] : 'General'}</span>
                      <span className="frame-pill" style={{ color: sentColor, borderColor: sentColor }}>Tone: {sentLabel}</span>
                      {art.loaded_language_density >= 0.1 && (
                        <span className="frame-pill" style={{ color: 'var(--red)' }}>
                          Loaded: {art.loaded_language_density.toFixed(1)}/sent
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="article-body">
                    {art.sentences.map((sent, sIdx) => {
                      const quote = hlQuotes ? art.quotes.find(q => q.sentence_idx === sIdx) : null;
                      const hasClaim = hlClaims && art.claims.some(c => c.sentence_idx === sIdx);
                      return (
                        <div
                          key={sIdx}
                          className={`sentence-block${quote ? " has-quote" : hasClaim ? " has-claim" : ""}`}
                        >
                          {quote && (
                            <div className="quote-attribution">
                              {quote.speaker} · {quote.speaker_role}
                            </div>
                          )}
                          <span>{renderSentence(sent)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ── TAB: FRAMING ── */}
        {!loading && activeTab === "framing" && crossSource && (
          <div className="panel">
            <h2 className="panel-title">How each outlet framed the story</h2>
            <p className="panel-sub">
              News outlets emphasize different dimensions of an event. The percentages below show what proportion of each outlet's language fell into each framing category.
            </p>
            <div className="framing-grid">
              {FRAME_INFO.map((frame, fIdx) => (
                <div key={fIdx} className="frame-card">
                  <div className="frame-name">{frame.name}</div>
                  <p className="frame-desc">{frame.desc}</p>
                  {crossSource.sources_analyzed.map((src, sIdx) => {
                    const weight = crossSource.framing_divergence_matrix[src]?.[frame.name] || 0;
                    const pct = Math.round(weight * 100);
                    return (
                      <div key={sIdx} className="bar-row">
                        <div className="bar-label-row">
                          <span>{src}</span>
                          <span className="bar-label-pct">{pct}%</span>
                        </div>
                        <div className="bar-track">
                          <div
                            className="bar-fill"
                            style={{
                              width: `${pct}%`,
                              background: BAR_COLORS[sIdx % BAR_COLORS.length]
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── TAB: SENTIMENT ── */}
        {!loading && activeTab === "sentiment" && crossSource && articles.length > 0 && (
          <div className="panel">
            <h2 className="panel-title">Sentiment & tone comparison</h2>
            <p className="panel-sub">
              How positive, negative, or neutral is each outlet's language overall? Tone divergence is one of the clearest signals of framing bias.
            </p>
            <div className="framing-grid-wide">
              {/* Sentiment bars */}
              {['positive_ratio','negative_ratio','neutral_ratio'].map((key, kIdx) => {
                const label = key === 'positive_ratio' ? 'Positive' : key === 'negative_ratio' ? 'Negative' : 'Neutral';
                const color = key === 'positive_ratio' ? 'var(--green)' : key === 'negative_ratio' ? 'var(--red)' : 'var(--text-faint)';
                return (
                  <div key={kIdx} className="frame-card">
                    <div className="frame-name" style={{ color }}>{label} Tone</div>
                    <p className="frame-desc">% of sentences with {label.toLowerCase()} sentiment</p>
                    {articles.map((art, aIdx) => {
                      const val = art.aggregate_sentiment?.[key] || 0;
                      const pct = Math.round(val * 100);
                      return (
                        <div key={aIdx} className="bar-row">
                          <div className="bar-label-row"><span>{art.source}</span><span className="bar-label-pct">{pct}%</span></div>
                          <div className="bar-track"><div className="bar-fill" style={{ width: `${pct}%`, background: color }} /></div>
                        </div>
                      );
                    })}
                  </div>
                );
              })}
              {/* Emotion breakdown */}
              {['Anger','Fear','Joy','Sadness'].map((emo, eIdx) => {
                const eColor = emo==='Anger'?'#dc2626':emo==='Fear'?'#7c3aed':emo==='Joy'?'#16a34a':'#2563eb';
                return (
                  <div key={eIdx} className="frame-card">
                    <div className="frame-name" style={{ color: eColor }}>{emo}</div>
                    <p className="frame-desc">Proportion of {emo.toLowerCase()} signals detected</p>
                    {articles.map((art, aIdx) => {
                      const val = art.aggregate_emotions?.[emo] || 0;
                      const pct = Math.round(val * 100);
                      return (
                        <div key={aIdx} className="bar-row">
                          <div className="bar-label-row"><span>{art.source}</span><span className="bar-label-pct">{pct}%</span></div>
                          <div className="bar-track"><div className="bar-fill" style={{ width: `${pct}%`, background: eColor }} /></div>
                        </div>
                      );
                    })}
                  </div>
                );
              })}
              {/* Stance */}
              {['support','oppose','neutral'].map((stance, sIdx) => {
                const sColor = stance==='support'?'var(--green)':stance==='oppose'?'var(--red)':'var(--text-faint)';
                return (
                  <div key={sIdx} className="frame-card">
                    <div className="frame-name" style={{ color: sColor }}>Stance: {stance.charAt(0).toUpperCase()+stance.slice(1)}</div>
                    <p className="frame-desc">How often the article's sentences {stance === 'support' ? 'endorse' : stance === 'oppose' ? 'oppose or criticize' : 'take no clear position on'} the subject</p>
                    {articles.map((art, aIdx) => {
                      const val = art.aggregate_stance?.[stance] || 0;
                      const pct = Math.round(val * 100);
                      return (
                        <div key={aIdx} className="bar-row">
                          <div className="bar-label-row"><span>{art.source}</span><span className="bar-label-pct">{pct}%</span></div>
                          <div className="bar-track"><div className="bar-fill" style={{ width: `${pct}%`, background: sColor }} /></div>
                        </div>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── TAB: CLAIM CONCORDANCE ── */}
        {!loading && activeTab === "claims" && crossSource && (
          <div className="panel">
            <h2 className="panel-title">Claim concordance & divergence</h2>
            <p className="panel-sub">
              When two outlets cover the same sub-topic, do they agree or contradict each other? Diverging claims are the clearest evidence of factual framing differences.
            </p>
            {crossSource.claim_comparisons?.length > 0 ? (
              <div className="omission-list">
                {crossSource.claim_comparisons.map((cmp, idx) => {
                  const relColor = cmp.relation === 'concordant' ? 'var(--green)' : cmp.relation === 'diverging' ? 'var(--red)' : 'var(--amber)';
                  const relLabel = cmp.relation === 'concordant' ? 'Agree' : cmp.relation === 'diverging' ? 'Contradict' : 'Uncorroborated';
                  return (
                    <div key={idx} className="omission-item" style={{ borderLeft: `3px solid ${relColor}` }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
                        <span className="tag" style={{ background: relColor + '18', color: relColor }}>{relLabel}</span>
                        <span style={{ fontSize: '0.72rem', color: 'var(--text-faint)' }}>{Math.round(cmp.similarity_score * 100)}% similarity</span>
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
                        <div>
                          <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-faint)', marginBottom: '0.3rem' }}>
                            {cmp.source_a}
                          </div>
                          <p style={{ fontSize: '0.82rem', color: 'var(--text)', lineHeight: 1.55 }}>"{cmp.claim_a?.text}"</p>
                        </div>
                        {cmp.claim_b ? (
                          <div>
                            <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-faint)', marginBottom: '0.3rem' }}>
                              {cmp.source_b}
                            </div>
                            <p style={{ fontSize: '0.82rem', color: 'var(--text)', lineHeight: 1.55 }}>"{cmp.claim_b?.text}"</p>
                          </div>
                        ) : (
                          <div style={{ fontSize: '0.82rem', color: 'var(--text-faint)', fontStyle: 'italic', paddingTop: '1rem' }}>No matching claim found in {cmp.source_b || 'other outlet'}</div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p style={{ color: 'var(--text-faint)', fontSize: '0.85rem' }}>No cross-outlet claim comparisons detected.</p>
            )}
          </div>
        )}

        {/* ── TAB: OMISSIONS ── */}
        {!loading && activeTab === "omissions" && crossSource && (
          <div className="panel">
            <h2 className="panel-title">What was left out?</h2>
            <p className="panel-sub">
              One of the most powerful forms of bias is omission — leaving out key facts entirely. These are facts reported by some outlets but absent from others.
            </p>
            <div className="omission-list">
              {crossSource.omissions.map((om, idx) => (
                <div key={idx} className="omission-item">
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-faint)' }}>Omission #{idx + 1}</span>
                    <span style={{ fontSize: '0.7rem', color: om.salience_score >= 0.85 ? 'var(--red)' : 'var(--amber)' }}>
                      Salience: {om.salience_score >= 0.85 ? 'High' : 'Medium'}
                    </span>
                  </div>
                  <p className="omission-quote">"{om.representative_sentence}"</p>
                  <div className="omission-meta">
                    <div>
                      <span className="omission-meta-label">Reported by</span>
                      {om.reported_by.map((r, i) => (
                        <span key={i} className="tag tag-green" style={{ marginRight: 4 }}>✓ {r}</span>
                      ))}
                    </div>
                    <div>
                      <span className="omission-meta-label">Left out by</span>
                      {om.omitted_by.map((o, i) => (
                        <span key={i} className="tag tag-red" style={{ marginRight: 4 }}>✕ {o}</span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
              {crossSource.omissions.length === 0 && (
                <p style={{ color: "var(--text-faint)", fontSize: "0.85rem" }}>No significant omissions detected.</p>
              )}
            </div>
          </div>
        )}

        {/* ── TAB: SOURCING ── */}
        {!loading && activeTab === "sourcing" && crossSource && (
          <div className="panel">
            <h2 className="panel-title">Who gets quoted?</h2>
            <p className="panel-sub">
              Outlets can exhibit bias through whose voices they amplify — government officials, corporate executives, or independent citizens.
            </p>
            <div className="sourcing-grid">
              {crossSource.speaker_balance.map((stat, idx) => (
                <div key={idx} className="source-card">
                  <div className="source-card-header">
                    <div className="source-card-name">{stat.source}</div>
                    <span className="quote-count-badge">{stat.total_quotes} quotes</span>
                  </div>
                  <div style={{ marginBottom: "0.9rem" }}>
                    <div style={{ fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-faint)", marginBottom: "0.4rem" }}>
                      By role
                    </div>
                    {Object.entries(stat.role_distribution).map(([role, cnt], rIdx) => (
                      <div key={rIdx} className="role-row">
                        <span>{role}</span>
                        <span className="role-count">{cnt}</span>
                      </div>
                    ))}
                  </div>
                  {stat.top_speakers?.length > 0 && (
                    <div>
                      <div style={{ fontSize: "0.7rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-faint)", marginBottom: "0.4rem" }}>
                        Top speakers
                      </div>
                      {stat.top_speakers.map((spk, sIdx) => (
                        <div key={sIdx} className="speaker-item">
                          <span className="speaker-name">{spk.name}</span>
                          <span>{spk.count} quote{spk.count !== 1 ? "s" : ""}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {/* Official dominance ratio */}
                  {stat.official_dominance_ratio !== undefined && (
                    <div style={{ marginTop: '0.8rem', paddingTop: '0.6rem', borderTop: '1px solid var(--border)' }}>
                      <div style={{ fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-faint)', marginBottom: '0.4rem' }}>Official voice dominance</div>
                      <div className="bar-track" style={{ marginBottom: '0.25rem' }}>
                        <div className="bar-fill" style={{ width: `${Math.round(stat.official_dominance_ratio * 100)}%`, background: stat.official_dominance_ratio > 0.7 ? 'var(--red)' : 'var(--blue)' }} />
                      </div>
                      <div style={{ fontSize: '0.72rem', color: stat.official_dominance_ratio > 0.7 ? 'var(--red)' : 'var(--text-muted)' }}>
                        {Math.round(stat.official_dominance_ratio * 100)}% official/government sources
                        {stat.official_dominance_ratio > 0.7 ? ' — high authority bias' : ''}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── TAB: SEARCH ── */}
        {!loading && activeTab === "search" && (
          <div className="panel">
            <h2 className="panel-title">Search across all articles</h2>
            <p className="panel-sub">
              Ask a question to retrieve and compare how different outlets addressed the same topic using semantic similarity.
            </p>
            <form className="search-form" onSubmit={handleSearch}>
              <input
                className="search-input"
                type="text"
                placeholder='e.g. "What are the compliance costs?" or "Who warned about job losses?"'
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
              <button type="submit" className="btn btn-primary" disabled={searchLoading}>
                {searchLoading ? "Searching…" : "Search"}
              </button>
            </form>

            {searchResult && (
              <div>
                <div className="search-result-summary">
                  <div className="search-result-label">Cross-outlet synthesis</div>
                  {searchResult.contrastive_explanation}
                </div>
                <div className="evidence-list">
                  {searchResult.retrieved_evidence.map((p, idx) => (
                    <div key={idx} className="evidence-item">
                      <div className="evidence-item-header">
                        <span className="evidence-source">{p.source}</span>
                        <span className="evidence-match">{Math.round(p.similarity_score * 100)}% match</span>
                      </div>
                      <p className="evidence-text">"{p.sentence_text}"</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── TAB: ENTITIES ── */}
        {!loading && activeTab === "entities" && articles.length > 0 && (
          <div className="panel">
            <h2 className="panel-title">Named entities mentioned</h2>
            <p className="panel-sub">
              Who and what does each outlet mention most? Differences in entity focus reveal selective emphasis — e.g. one outlet naming specific officials while another stays abstract.
            </p>
            <div className="framing-grid-wide">
              {articles.map((art, aIdx) => (
                <div key={aIdx} className="frame-card">
                  <div className="frame-name" style={{ marginBottom: '0.8rem' }}>{art.source}</div>
                  {['PERSON','ORG','GPE','LAW/TREATY','NUMBER'].map(label => {
                    const group = art.entities?.filter(e => e.label === label) || [];
                    if (group.length === 0) return null;
                    const labelName = label === 'PERSON' ? 'People' : label === 'ORG' ? 'Organisations' : label === 'GPE' ? 'Places' : label === 'LAW/TREATY' ? 'Laws & Treaties' : 'Statistics & Figures';
                    const labelColor = label === 'NUMBER' ? 'var(--blue)' : label === 'PERSON' ? 'var(--text)' : 'var(--text-muted)';
                    return (
                      <div key={label} style={{ marginBottom: '0.8rem' }}>
                        <div style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--text-faint)', marginBottom: '0.35rem' }}>
                          {labelName}
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
                          {group.slice(0, 8).map((ent, eIdx) => (
                            <span key={eIdx} style={{
                              fontSize: '0.73rem', padding: '0.15rem 0.5rem',
                              borderRadius: '3px', border: '1px solid var(--border)',
                              background: 'var(--bg-input)', color: 'var(--text-muted)',
                              display: 'inline-flex', alignItems: 'center', gap: '0.3rem'
                            }}>
                              {ent.text}
                              <span style={{ color: 'var(--text-faint)', fontSize: '0.65rem' }}>×{ent.count}</span>
                            </span>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                  {(!art.entities || art.entities.length === 0) && (
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-faint)' }}>No named entities detected.</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

      </main>

      {/* Add Articles Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <span className="modal-title">Add articles to compare</span>
              <button className="btn btn-ghost" style={{ padding: "0.3rem 0.6rem" }} onClick={() => setShowModal(false)}>
                Close
              </button>
            </div>

            <div className="modal-body">
              {/* URL scraper */}
              <div className="scrape-row">
                <input
                  className="field-input"
                  type="text"
                  placeholder="Paste a news URL to auto-import…"
                  value={scrapeUrl}
                  onChange={e => setScrapeUrl(e.target.value)}
                />
                <button className="btn btn-ghost" onClick={handleScrape} disabled={scraping}>
                  {scraping ? "Importing…" : "Import"}
                </button>
              </div>

              {customArticles.map((art, idx) => (
                <div key={idx} className="article-form-block">
                  <div className="article-form-label">
                    Article {idx + 1}
                    {customArticles.length > 2 && (
                      <button
                        style={{ background: "none", border: "none", color: "var(--red)", fontSize: "0.75rem", cursor: "pointer" }}
                        onClick={() => setCustomArticles(customArticles.filter((_, i) => i !== idx))}
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "0.5rem", marginBottom: "0.5rem" }}>
                    <input
                      className="field-input"
                      type="text"
                      placeholder="Source (e.g. CNN)"
                      value={art.source}
                      onChange={e => {
                        const copy = [...customArticles];
                        copy[idx].source = e.target.value;
                        setCustomArticles(copy);
                      }}
                    />
                    <input
                      className="field-input"
                      type="text"
                      placeholder="Headline"
                      value={art.title}
                      onChange={e => {
                        const copy = [...customArticles];
                        copy[idx].title = e.target.value;
                        setCustomArticles(copy);
                      }}
                    />
                  </div>
                  <textarea
                    className="field-textarea"
                    rows={3}
                    placeholder="Paste article text here…"
                    value={art.content}
                    onChange={e => {
                      const copy = [...customArticles];
                      copy[idx].content = e.target.value;
                      setCustomArticles(copy);
                    }}
                  />
                </div>
              ))}
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-ghost"
                onClick={() => setCustomArticles([...customArticles, { title: "", source: `Outlet ${customArticles.length + 1}`, content: "", url: "" }])}
              >
                Add another outlet
              </button>
              <button className="btn btn-primary" onClick={handleCustomSubmit}>
                Run analysis
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
