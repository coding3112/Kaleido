import os
from collections import defaultdict
from datetime import date
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from retrieval import search_articles

app = FastAPI(title="Kaleido API", version="0.2.0")

# In local development Vite proxies /api to localhost:8000.
# In production, set FRONTEND_ORIGIN to the deployed frontend URL.
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
allowed_origins = [origin.strip() for origin in frontend_origin.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    scope: str = "all"
    depth: int = Field(default=15, ge=1, le=50)
    hybrid: bool = True
    maxPerspectives: str = "auto"

@app.get("/")
def root():
    return {"name": "Kaleido API", "status": "running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "running"}

@app.post("/api/report")
def make_report(request: ReportRequest):
    question = request.question.strip()
    if len(question) < 5:
        raise HTTPException(status_code=422, detail="Please enter a longer topic.")

    if request.scope not in {"all", "news", "research"}:
        raise HTTPException(status_code=422, detail="scope must be all, news, or research.")

    # This prototype uses local keyword retrieval; it does not call an LLM or live news API.
    found = search_articles(question)
    if request.scope != "all":
        found = [
            article for article in found
            if article.get("source_type", "").lower() == request.scope
        ]
    found = found[:request.depth]
    if not found:
        raise HTTPException(
            status_code=404,
            detail="No matching articles were found in Kaleido's small sample dataset. Try 'solar energy' or add more articles to backend/data/articles.json."
        )

    sources = []
    evidence = []
    grouped = defaultdict(list)
    for index, article in enumerate(found, start=1):
        sid = f"s{index}"
        eid = f"e{index}"
        perspective = str(article.get("perspective", "mixed")).lower()
        if perspective in {"supportive", "support", "positive"}:
            pkey = "supportive"
        elif perspective in {"critical", "oppose", "negative"}:
            pkey = "critical"
        else:
            pkey = "balanced"

        sources.append({
            "id": sid,
            "title": article.get("title", "Untitled source"),
            "publisher": article.get("source", "Unspecified source"),
            "author": "",
            "type": article.get("source_type", "research"),
            "url": article.get("url", ""),
            "retrieved": date.today().strftime("%b %d, %Y"),
            "license": "Not specified in sample dataset",
        })
        evidence.append({
            "id": eid,
            "source_id": sid,
            "relevance": 0.5,
            "passage": article.get("text", ""),
        })
        grouped[pkey].append((article, eid))

    labels = {
        "supportive": ("Supportive", "Arguments or evidence describing potential benefits."),
        "critical": ("Critical", "Arguments or evidence describing limitations, costs, or risks."),
        "balanced": ("Mixed / other", "Sources that present mixed, contextual, or not-yet-classified perspectives."),
    }
    perspectives = []
    for key in ("supportive", "critical", "balanced"):
        items = grouped.get(key, [])
        if not items:
            continue
        perspectives.append({
            "key": key,
            "label": labels[key][0],
            "stance": labels[key][1],
            "points": [item[0].get("title", "Untitled source") for item in items[:3]],
            "evidence": "limited",
            "sources_count": len(items),
            "details": "This grouping is based on the sample dataset's perspective labels. It is a prototype classification, not an independent fact-check.",
        })

    return {
        "id": str(uuid4()),
        "question": question,
        "scope": request.scope,
        "searched_on": date.today().strftime("%b %d, %Y"),
        "source_total": len(sources),
        "summary": (
            f"Kaleido found {len(sources)} matching item(s) in its local sample dataset for “{question}”. "
            "This prototype retrieves passages by keyword overlap and groups them using the dataset's existing perspective labels. "
            "It does not yet generate an AI-written synthesis or independently verify claims."
        ),
        "reading_minutes": max(1, round(sum(len(s.get("title", "")) for s in sources) / 900)),
        "perspectives": perspectives,
        "agreement": [],
        "disagreement": [],
        "uncertainty": [{
            "text": "The current sample dataset is small; broader conclusions require more sources and a stronger evidence-analysis pipeline.",
            "claims": [],
        }],
        "claims": [],
        "evidence": evidence,
        "sources": sources,
        "mock": False,
    }
