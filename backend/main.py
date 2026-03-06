from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline import run_pipeline

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Retrieve the keyword from the input (will be the app)
@app.get("/analyze/{keyword}")

# Now send the keyword through the pipeline (pipeline.py)
async def analyze(keyword: str, num_articles: int = 10):
    results = run_pipeline(keyword, num_articles)
    # Return the keyword and a list of the articles
    return {"keyword": keyword, "articles": results}