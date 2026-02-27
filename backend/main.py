from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline import run_pipeline

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.get("/analyze/{keyword}")
async def analyze(keyword: str, num_articles: int = 10):
    results = run_pipeline(keyword, num_articles)
    return {"keyword": keyword, "articles": results}