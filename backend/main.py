import asyncio
import json
import sys

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


@app.get("/analyze/{keyword}")
async def analyze(keyword: str, num_articles: int = Query(default=10, ge=1, le=50)):
    try:
        results = await asyncio.to_thread(run_pipeline, keyword, num_articles)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"keyword": keyword, "articles": results}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        keyword = " ".join(sys.argv[1:])
    else:
        keyword = input("Enter keyword to analyze: ").strip()

    num_articles = 5

    print(f"\nAnalyzing '{keyword}' — fetching {num_articles} articles...\n")

    results = run_pipeline(keyword, num_articles)

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

    # Optionally dump full JSON to a file for inspection
    with open("test_output.json", "w") as f:
        json.dump({"keyword": keyword, "articles": results}, f, indent=2)
    print("Full output saved to test_output.json")