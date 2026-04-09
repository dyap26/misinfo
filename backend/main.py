import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
import asyncio
import json
import sys
import argparse
from urllib.parse import urlparse

from scraper import get_full_text
from scorer import score_article
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pipeline import run_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return "Unknown"


@app.post("/analyze/url")
async def analyze_url(payload: dict):
    url = payload.get("url", "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        content = get_full_text(url)
        status = "ok" if content else "scrape_failed"

        article = {
            "title": payload.get("title", "User-submitted article"),
            "source": _extract_domain(url),
            "url": url,
            "content": content or "",
            "scrape_status": status,
        }

        if not content:
            raise HTTPException(status_code=422, detail="Could not extract content from URL")

        result = score_article(article)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analyze/{keyword}")
async def analyze(
    keyword: str,
    num_articles: int = Query(default=10, ge=1, le=50),
    category: str = Query(default=None, enum=["business", "entertainment", "general", "health", "science", "sports", "technology"])
):
    try:
        results = await asyncio.to_thread(run_pipeline, keyword, num_articles, category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"keyword": keyword, "articles": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Misinformation analyzer")
    parser.add_argument("keyword", nargs="*", help="Keyword to analyze")
    parser.add_argument("--category", choices=["business", "entertainment", "general", "health", "science", "sports", "technology"], default=None)
    parser.add_argument("--num-articles", type=int, default=5)
    args = parser.parse_args()

    keyword = " ".join(args.keyword) if args.keyword else input("Enter keyword to analyze: ").strip()
    num_articles = args.num_articles

    print(f"\nAnalyzing '{keyword}' — fetching {num_articles} articles...\n")

    results = run_pipeline(keyword, num_articles, args.category)

    for i, article in enumerate(results, 1):
        print(f"{'='*60}")
        print(f"[{i}] {article.get('title', 'No title')}")
        print(f"    Source         : {article.get('source', 'Unknown')}")
        print(f"    Score          : {article.get('overall_score', 'N/A')}/10")
        print(f"    Classification : {article.get('classification', 'N/A').upper()}")
        print(f"    Reasoning      : {article.get('reasoning', 'N/A')}")
        if article.get("red_flags"):
            print(f"    ⚠ Red Flags   : {', '.join(article['red_flags'])}")
        if article.get("strengths"):
            print(f"    ✓ Strengths   : {', '.join(article['strengths'])}")
        print(f"    URL            : {article.get('url', 'N/A')}")

    print(f"\n{'='*60}")
    print(f"Done. {len(results)} articles analyzed.")