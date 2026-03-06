from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
import logging
import time

from fetch_articles import fetch_articles
from scraper import get_full_text  # use the improved version with paywall handling
from scorer import score_article

logger = logging.getLogger(__name__)

# LLM APIs will rate-limit you if you fire 10 requests instantly
SCORER_RATE_LIMIT_DELAY = 0.2  # seconds between scoring requests

def _scrape_article(article: dict) -> dict:
    """Scrape one article, return it enriched. Never raises."""
    try:
        text = get_full_text(article)
        article["content"] = text or article.get("content") or article.get("description") or ""
    except Exception as e:
        logger.warning(f"Scrape failed for {article.get('url')}: {e}")
        article["content"] = article.get("description") or ""
    return article


def _score_article_safe(article: dict) -> Optional[dict]:
    """Score one article. Returns None on failure so pipeline keeps running."""
    try:
        return score_article(article)
    except Exception as e:
        logger.warning(f"Scoring failed for '{article.get('title')}': {e}")
        return None


def run_pipeline(keyword: str, num_articles: int = 10) -> list[dict]:
    """
    Full pipeline: fetch → scrape → score → rank.
    - Scraping is parallelized (I/O bound)
    - Scoring is rate-limited to avoid LLM API throttling
    """
    logger.info(f"Starting pipeline for keyword: '{keyword}'")

    # Step 1: Fetch
    articles = fetch_articles(keyword, num_articles)
    if not articles:
        logger.warning("No articles returned from fetch.")
        return []

    # Step 2: Scrape concurrently (I/O bound — threads are fine)
    with ThreadPoolExecutor(max_workers=5) as executor:
        enriched = list(executor.map(_scrape_article, articles))

    # Filter out articles with no usable content before scoring
    enriched = [a for a in enriched if len(a.get("content", "")) > 50]
    logger.info(f"Scraping complete. {len(enriched)}/{len(articles)} articles have content.")

    # Step 3: Score with rate limiting
    # ThreadPoolExecutor is fine here but we stagger submissions to avoid burst
    scored = []
    failed = 0

    with ThreadPoolExecutor(max_workers=3) as executor:  # lower than scraping — LLM has rate limits
        futures = {}
        for i, article in enumerate(enriched):
            future = executor.submit(_score_article_safe, article)
            futures[future] = article
            time.sleep(SCORER_RATE_LIMIT_DELAY)  # stagger API calls

        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                scored.append(result)
            else:
                failed += 1

    logger.info(f"Scoring complete. {len(scored)} scored, {failed} failed.")

    # Step 4: Sort — credible articles first, misinformation last
    scored.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

    return scored