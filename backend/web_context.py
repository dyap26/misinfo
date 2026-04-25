import httpx
import os
import logging

logger = logging.getLogger(__name__)


def fetch_web_context(topic: str, max_chars: int = 1500) -> str:
    """
    Fetch a real-time summary for a topic using Tavily Search.
    Used to ground the scorer against post-cutoff events.
    Returns an empty string on failure — scorer degrades gracefully.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.warning("TAVILY_API_KEY not set — skipping web context")
        return ""

    try:
        response = httpx.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": topic,
                "search_depth": "basic",
                "max_results": 3,
                "include_answer": True,  # Tavily synthesizes a summary — ideal for prompts
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()

        # Prefer the synthesized answer if Tavily provides one
        if data.get("answer"):
            return data["answer"][:max_chars]

        # Fall back to stitching result snippets
        snippets = [
            r.get("content", "")
            for r in data.get("results", [])
            if r.get("content")
        ]
        return " ".join(snippets)[:max_chars]

    except httpx.HTTPStatusError as e:
        logger.warning(f"Tavily HTTP error for '{topic}': {e.response.status_code}")
        return ""
    except Exception as e:
        logger.warning(f"Tavily fetch failed for '{topic}': {e}")
        return ""