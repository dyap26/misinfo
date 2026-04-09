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

def get_full_text(url: str, char_limit: int = 3000) -> tuple[str, str]:
    if not isinstance(url, str):
        return "", "scrape_failed"
    if not url.startswith(("http://", "https://")):
        return "", "scrape_failed"

    try:
        response = httpx.get(url, headers=HEADERS, timeout=10, follow_redirects=True)
        response.raise_for_status()

        article = Article(url)
        article.download(input_html=response.text)  # ← replaces set_html
        article.parse()

        text = article.text.strip()

        if any(sig in text.lower() for sig in SCRAPE_FAILURE_SIGNALS):
            return article.meta_description or "", "scrape_failed"

        if len(text) < 100:
            return article.meta_description or "", "scrape_failed"

        if is_likely_paywalled(text):
            return article.meta_description or "", "paywall"

        return text[:char_limit], "ok"

    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return "", "scrape_failed"