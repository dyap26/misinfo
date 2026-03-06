import requests

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_articles(keyword: str, num_articles: int = 10):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": keyword,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": num_articles,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params=params)
    articles = response.json().get("articles", [])
    
    return [
        {
            "title": a["title"],
            "source": a["source"]["name"],
            "description": a["description"],
            "url": a["url"],
            "content": a["content"],
            "publishedAt": a["publishedAt"]
        }
        for a in articles if a["content"]
    ]