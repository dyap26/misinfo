import httpx
from newspaper import Article
import logging

logger = logging.getLogger(__name__)

def get_full_text(url: str, char_limit: int = 3000) -> str:
    """
    Fetch and parse full article text from a URL.
    Returns empty string on failure rather than crashing the pipeline.
    """
    if not url or not url.startswith(("http://", "https://")):
        return ""

    try:
        article = Article(url, request_timeout=10)
        article.download()
        article.parse()

        text = article.text.strip()

        if len(text) < 100:
            # Likely a paywalled, JS-rendered, or bot-blocked page
            logger.warning(f"Suspiciously short content from {url} ({len(text)} chars)")
            return article.meta_description or ""  # fall back to meta description

        return text[:char_limit]

    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return ""