import httpx
from bs4 import BeautifulSoup
import logging
import json
import re
from datetime import datetime

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

def _parse_date_string(raw: str) -> str | None:
    """
    Attempt to parse a raw date string into YYYY-MM-DD.
    Returns None if unparseable.
    """
    if not raw:
        return None
    raw = raw.strip()
    # Truncate to date portion if ISO datetime (2024-03-15T10:30:00Z -> 2024-03-15)
    iso_match = re.match(r"(\d{4}-\d{2}-\d{2})", raw)
    if iso_match:
        return iso_match.group(1)
    # Try common formats
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def _extract_date_from_soup(soup: BeautifulSoup) -> str | None:
    """
    Try multiple strategies to extract a publication date from a parsed page.
    Returns a YYYY-MM-DD string or None.
    """
    # 1. JSON-LD structured data (most reliable)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            # Handle both single object and @graph array
            candidates = data if isinstance(data, list) else [data]
            for item in candidates:
                if isinstance(item, dict):
                    # Unwrap @graph
                    if "@graph" in item:
                        candidates += item["@graph"]
                        continue
                    for field in ("datePublished", "dateCreated", "uploadDate"):
                        if field in item:
                            parsed = _parse_date_string(str(item[field]))
                            if parsed:
                                return parsed
        except (json.JSONDecodeError, AttributeError):
            continue

    # 2. <meta> tags
    meta_names = [
        ("property", "article:published_time"),
        ("name", "article:published_time"),
        ("name", "date"),
        ("name", "pubdate"),
        ("name", "publish-date"),
        ("name", "publication_date"),
        ("name", "DC.date"),
        ("itemprop", "datePublished"),
        ("property", "og:article:published_time"),
    ]
    for attr, value in meta_names:
        tag = soup.find("meta", attrs={attr: value})
        if tag:
            parsed = _parse_date_string(tag.get("content", ""))
            if parsed:
                return parsed

    # 3. <time> element with datetime attribute
    time_tag = soup.find("time", attrs={"datetime": True})
    if time_tag:
        parsed = _parse_date_string(time_tag["datetime"])
        if parsed:
            return parsed

    # 4. Common CSS class/itemprop selectors used by news sites
    selectors = [
        {"itemprop": "datePublished"},
        {"class": re.compile(r"publish(ed)?[_-]?(date|time)", re.I)},
        {"class": re.compile(r"(article|post)[_-]?date", re.I)},
        {"class": re.compile(r"date[_-]?(published|posted)", re.I)},
    ]
    for attrs in selectors:
        tag = soup.find(attrs=attrs)
        if tag:
            # Prefer datetime attr, fall back to text content
            raw = tag.get("datetime") or tag.get_text(strip=True)
            parsed = _parse_date_string(raw)
            if parsed:
                return parsed

    return None

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

def get_full_text(url: str, char_limit: int = 3000) -> tuple[str, str | None]:
    """
    Returns (text, published_date).
    published_date is a YYYY-MM-DD string or None if not found.
    """
    if not isinstance(url, str):
        return "", None
    if not url.startswith(("http://", "https://")):
        return "", None

    try:
        response = httpx.get(url, headers=HEADERS, timeout=10, follow_redirects=True)

        if response.status_code == 403:
            logger.warning(f"403 Forbidden for {url}")
            return "", None

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        published_date = _extract_date_from_soup(soup)
        text = _extract_text(soup)
        meta = _extract_meta(soup)

        if len(text) < 100:
            logger.warning(f"Short content from {url} ({len(text)} chars) — likely blocked")
            return meta, published_date

        if is_likely_paywalled(text):
            logger.warning(f"Paywall detected at {url}")
            return meta, published_date

        return text[:char_limit], published_date

    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return "", None