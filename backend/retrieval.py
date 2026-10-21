import json
import re
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "articles.json"
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "in", "on", "at", "to", "of", "for", "and", "or", "but", "with", "by",
    "from", "as", "it", "its", "this", "that", "these", "those", "what",
    "why", "how", "can", "could", "should", "would", "do", "does", "did",
    "about", "into", "than", "their", "they", "them", "we", "you", "your", "i",
}

def tokenize(text: str) -> list[str]:
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 1]

def load_articles() -> list[dict]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Article dataset not found: {DATA_FILE}")
    with DATA_FILE.open("r", encoding="utf-8") as file:
        articles = json.load(file)
    if not isinstance(articles, list):
        raise ValueError("Article dataset must be a JSON list.")
    return articles

def search_articles(query: str) -> list[dict]:
    query_words = set(tokenize(query))
    if not query_words:
        return []
    results = []
    for article in load_articles():
        title = article.get("title", "")
        content = article.get("text", article.get("content", ""))
        article_words = set(tokenize(f"{title} {content}"))
        title_words = set(tokenize(title))
        matched = query_words.intersection(article_words)
        if not matched:
            continue
        score = len(matched) + 2 * len(query_words.intersection(title_words))
        results.append({
            **article,
            "retrieval_score": round(score / max(1, len(query_words)), 4),
            "matched_terms": sorted(matched),
        })
    results.sort(key=lambda item: item["retrieval_score"], reverse=True)
    return results
