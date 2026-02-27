# backend/scraper.py
from newspaper3k import Article

def get_full_text(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text[:3000]  # cap tokens
    except Exception:
        return ""