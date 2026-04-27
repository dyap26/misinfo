import chromadb
import logging
import re
import os
from chromadb.utils import embedding_functions
from collections import Counter

logger = logging.getLogger(__name__)

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = "source_history"

_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


# --- Helpers ---

def _clean_source(source: str | None) -> str:
    """
    Strip markdown hyperlinks that terminals inject into domain strings.
    e.g. '[foxnews.com](http://foxnews.com)' -> 'foxnews.com'
    """
    if not source:
        return "unknown"
    match = re.match(r'\[([^\]]+)\]\([^)]+\)', source)
    return match.group(1) if match else source


# --- Public API ---

def record_source(article: dict) -> None:
    """
    Persist a scored article into the source history ledger.
    Keyed by URL - safe to call multiple times (upsert).
    """
    url = article.get("url", "").strip()
    source = _clean_source(article.get("source", "").strip())
    if not url:
        logger.debug("Skipping record_source - no URL on article")
        return

    doc_text = f"{article.get('title', '')} {article.get('content', '')[:500]}"

    try:
        _collection.upsert(
            ids=[url],
            documents=[doc_text],
            metadatas=[{
                "source": source,
                "overall_score": str(article.get("overall_score", 0)),
                "classification": article.get("classification", "unscored"),
                "title": article.get("title", "")[:500],
            }],
        )
        logger.debug(f"Recorded source history for '{source}' - {url}")
    except Exception as e:
        logger.warning(f"Failed to record source '{source}': {e}")


def get_source_history(source: str) -> str:
    """
    Return a plain-text summary of all past scores for a given source name.
    Returns empty string if no history exists yet.
    """
    source = _clean_source(source)
    if not source or source == "unknown":
        return ""

    try:
        results = _collection.get(
            where={"source": {"$eq": source}},
            include=["metadatas"],
        )
        metas = results.get("metadatas") or []
        if not metas:
            return ""

        scores = [
            float(m["overall_score"])
            for m in metas
            if m.get("overall_score") not in (None, "", "0")
        ]
        classifications = [
            m["classification"]
            for m in metas
            if m.get("classification") and m["classification"] != "unscored"
        ]

        avg = round(sum(scores) / len(scores), 1) if scores else None
        top_class = Counter(classifications).most_common(1)[0][0] if classifications else None

        parts = [f"{source} has been scored {len(metas)} time(s) in this system."]
        if avg is not None:
            parts.append(f"Average credibility score: {avg}/10.")
        if scores:
            parts.append(f"Score range: {min(scores)}-{max(scores)}/10.")
        if top_class:
            parts.append(f"Most common classification: {top_class}.")
        if classifications:
            parts.append(f"Classification breakdown: {dict(Counter(classifications))}.")
        recent_titles = [m["title"] for m in metas[-3:] if m.get("title")]
        if recent_titles:
            parts.append(f"Recent articles scored: {'; '.join(recent_titles)}.")

        return " ".join(parts)

    except Exception as e:
        logger.warning(f"Failed to retrieve source history for '{source}': {e}")
        return ""


def collection_size() -> int:
    """Return total number of articles stored in source history."""
    try:
        return _collection.count()
    except Exception:
        return 0


def get_similar_articles(title: str, content: str, n: int = 3) -> str:
    """
    Semantic search: find past articles similar to the current one.
    Returns a plain-text summary for injection into the scoring prompt.
    """
    query = f"{title} {content[:300]}"
    try:
        results = _collection.query(
            query_texts=[query],
            n_results=n,
            include=["metadatas"],
        )
        metas = results.get("metadatas", [[]])[0]
        if not metas:
            return ""

        lines = ["Similar articles scored previously:"]
        for m in metas:
            lines.append(
                f"- '{m.get('title', 'Unknown')}' ({m.get('source', '?')}): "
                f"{m.get('overall_score', '?')}/10, {m.get('classification', '?')}"
            )
        return "\n".join(lines)

    except Exception as e:
        logger.warning(f"Semantic search failed: {e}")
        return ""