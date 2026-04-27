import os
import re
import logging
from datetime import date, timedelta

from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env.local")

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise EnvironmentError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env.local")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


# --- Helpers ---

def _clean_source(source: str | None) -> str | None:
    """
    Strip markdown hyperlinks that terminals inject into domain strings.
    e.g. '[foxnews.com](http://foxnews.com)' -> 'foxnews.com'
    """
    if not source:
        return source
    match = re.match(r'\[([^\]]+)\]\([^)]+\)', source)
    return match.group(1) if match else source


# --- Cache freshness ---

def needs_rescore(article_row: dict) -> bool:
    """
    Returns True if the cached score is stale and should be re-scored.

    Tier 1 - First 7 days after publication: re-score daily.
    Tier 2 - After 7 days (or unknown publish date): re-score weekly.
    """
    last_scored_raw = article_row.get("last_scored_at")
    published_raw   = article_row.get("published_date")
    today           = date.today()

    if last_scored_raw is None:
        return True
    if isinstance(last_scored_raw, str):
        last_scored = date.fromisoformat(last_scored_raw[:10])
    else:
        last_scored = last_scored_raw if isinstance(last_scored_raw, date) else last_scored_raw.date()

    published = None
    if published_raw:
        if isinstance(published_raw, str):
            published = date.fromisoformat(published_raw[:10])
        else:
            published = published_raw

    age_days = (today - published).days if published else None

    if age_days is not None and age_days <= 7:
        return last_scored < today
    else:
        return last_scored < today - timedelta(days=7)


# --- DB reads ---

def get_cached_article(url: str) -> dict | None:
    """
    Returns the cached DB row for the given URL, or None if not found.
    Does not apply freshness logic - call needs_rescore() separately.
    """
    try:
        res = supabase.table("articles").select("*").eq("url", url).single().execute()
        return res.data if res.data else None
    except Exception as e:
        logger.debug(f"Cache miss for {url}: {e}")
        return None


# --- DB writes ---

def upsert_article(result: dict) -> None:
    scores = result.get("scores", {})

    payload = {
        "url":            result.get("url"),
        "title":          result.get("title"),
        "source":         _clean_source(result.get("source")),
        "published_date": result.get("published_date"),
        "scrape_status":  result.get("scrape_status"),

        "overall_score":  result.get("overall_score"),
        "classification": result.get("classification"),
        "reasoning":      result.get("reasoning"),
        "red_flags":      result.get("red_flags", []),
        "strengths":      result.get("strengths", []),

        "score_source_reputation":   scores.get("source_reputation"),
        "score_evidence_quality":    scores.get("evidence_quality"),
        "score_factual_language":    scores.get("factual_language"),
        "score_balance":             scores.get("balance"),
        "score_logical_consistency": scores.get("logical_consistency"),
        "score_verifiability":       scores.get("verifiability"),
        "score_context_and_framing": scores.get("context_and_framing"),
    }

    try:
        supabase.rpc("upsert_article", {"payload": payload}).execute()
        logger.debug(f"Upserted article: {result.get('url')}")
    except Exception as e:
        logger.error(f"Failed to upsert article '{result.get('url')}': {e}")


# --- Cache reconstruction ---

def build_result_from_cache(article: dict, cached: dict) -> dict:
    """
    Reconstructs the standard scorer result shape from a cached DB row,
    merged with the live article metadata (title, content, etc.).
    """
    return {
        **article,
        "overall_score":  cached["overall_score"],
        "classification": cached["classification"],
        "reasoning":      cached["reasoning"],
        "red_flags":      cached["red_flags"] or [],
        "strengths":      cached["strengths"] or [],
        "scores": {
            "source_reputation":   cached["score_source_reputation"],
            "evidence_quality":    cached["score_evidence_quality"],
            "factual_language":    cached["score_factual_language"],
            "balance":             cached["score_balance"],
            "logical_consistency": cached["score_logical_consistency"],
            "verifiability":       cached["score_verifiability"],
            "context_and_framing": cached["score_context_and_framing"],
        },
        "_cache_hit": True,
    }