# backend/pipeline.py
from concurrent.futures import ThreadPoolExecutor
from fetch_articles import fetch_articles
from scraper import get_full_text
from scorer import score_article

def run_pipeline(keyword: str, num_articles: int = 10):
    articles = fetch_articles(keyword, num_articles)
    
    # Enrich with full text concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        full_texts = list(executor.map(
            lambda a: get_full_text(a["url"]), articles
        ))
    
    for article, text in zip(articles, full_texts):
        article["content"] = text or article["content"] or article["description"]
    
    # Score all articles concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        scored_articles = list(executor.map(score_article, articles))
    
    # Sort by overall_score descending
    scored_articles.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
    return scored_articles