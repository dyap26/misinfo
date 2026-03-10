import httpx
from newspaper import Article
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

PAYWALL_SIGNALS = [
    "subscribe to read",
    "create a free account",
    "sign in to read",
    "already a subscriber",
    "continue reading",
]

def is_likely_paywalled(text: str) -> bool:
    lowered = text.lower()
    return any(signal in lowered for signal in PAYWALL_SIGNALS)

def get_full_text(url: str, char_limit: int = 3000) -> str:
    if not isinstance(url, str):
        return ""
    if not url.startswith(("http://", "https://")):
        return ""

    try:
        # Use httpx to fetch with a real browser User-Agent
        response = httpx.get(url, headers=HEADERS, timeout=10, follow_redirects=True)
        response.raise_for_status()

        article = Article(url)
        article.set_html(response.text)  # feed pre-fetched HTML
        article.parse()

        text = article.text.strip()

        if len(text) < 100:
            logger.warning(f"Short content from {url} ({len(text)} chars) — likely blocked")
            return article.meta_description or ""

        if is_likely_paywalled(text):
            logger.warning(f"Paywall detected at {url}")
            return article.meta_description or ""

        return text[:char_limit]

    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return ""