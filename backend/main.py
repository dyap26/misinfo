from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline import run_pipeline
import json
import sys

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.get("/analyze/{keyword}")
async def analyze(keyword: str, num_articles: int = 10):
    results = run_pipeline(keyword, num_articles)
    return {"keyword": keyword, "articles": results}

# For testing purposes, uses command line instead of the app
if __name__ == "__main__":
    # Get keyword from command line arg, or prompt if none given
    if len(sys.argv) > 1:
        keyword = " ".join(sys.argv[1:])
    else:
        keyword = input("Enter keyword to analyze: ").strip()

    num_articles = 5 # Change this later during prod

    print(f"\nAnalyzing '{keyword}' — fetching {num_articles} articles...\n")

    results = run_pipeline(keyword, num_articles)

    for i, article in enumerate(results, 1):
        print(f"{'='*60}")
        print(f"[{i}] {article.get('title', 'No title')}")
        print(f"    Source      : {article.get('source', 'Unknown')}")
        print(f"    Score       : {article.get('overall_score', 'N/A')}/10")
        print(f"    Classification : {article.get('classification', 'N/A').upper()}")
        print(f"    Reasoning   : {article.get('reasoning', 'N/A')}")
        if article.get('red_flags'):
            print(f"    ⚠ Red Flags : {', '.join(article['red_flags'])}")
        if article.get('strengths'):
            print(f"    ✓ Strengths : {', '.join(article['strengths'])}")
        print(f"    URL         : {article.get('url', 'N/A')}")

    print(f"\n{'='*60}")
    print(f"Done. {len(results)} articles analyzed.")

    # Optionally dump full JSON to a file for inspection
    #with open("test_output.json", "w") as f:
        #json.dump({"keyword": keyword, "articles": results}, f, indent=2)
    #print("Full output saved to test_output.json")