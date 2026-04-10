import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

FALLBACK_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
}

PAYWALL_SIGNALS = [
    "subscribe to read",
    "create a free account",
    "sign in to read",
    "already a subscriber",
    "continue reading",
]

def is_likely_paywalled(text: str) -> bool:
    return any(signal in text.lower() for signal in PAYWALL_SIGNALS)

def _extract_meta(soup: BeautifulSoup) -> str:
    tag = (
        soup.find("meta", attrs={"name": "description"})
        or soup.find("meta", attrs={"property": "og:description"})
    )
    return tag.get("content", "").strip() if tag else ""

def _extract_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "iframe"]):
        tag.decompose()

    container = (
        soup.find("article")
        or soup.find("main")
        or soup.find(attrs={"role": "main"})
        or soup.find("body")
    )

    if not container:
        return ""

    paragraphs = container.find_all("p")
    return " ".join(p.get_text(separator=" ", strip=True) for p in paragraphs).strip()

def get_article_title(url: str) -> str:
    try:
        response = httpx.get(url, headers=HEADERS, timeout=10, follow_redirects=True)
        soup = BeautifulSoup(response.text, "lxml")
        tag = (
            soup.find("meta", attrs={"property": "og:title"})
            or soup.find("meta", attrs={"name": "title"})
        )
        if tag:
            return tag.get("content", "").strip()
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else ""
    except Exception:
        return ""

def get_full_text(url: str, char_limit: int = 3000) -> str:
    if not isinstance(url, str):
        return ""
    if not url.startswith(("http://", "https://")):
        return ""

    try:
        response = httpx.get(url, headers=HEADERS, timeout=10, follow_redirects=True)

        # Handles blocked
        if response.status_code == 403:
            response = httpx.get(url, headers=FALLBACK_HEADERS, timeout=10, follow_redirects=True)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        text = _extract_text(soup)
        meta = _extract_meta(soup)

        if len(text) < 100:
            logger.warning(f"Short content from {url} ({len(text)} chars) — likely blocked")
            return meta

        if is_likely_paywalled(text):
            logger.warning(f"Paywall detected at {url}")
            return meta

        return text[:char_limit]

    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return ""