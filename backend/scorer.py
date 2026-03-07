import anthropic
import json
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env.local")

logger = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SCORING_PROMPT = """
You are a media literacy expert. Analyze the following news article and rate its credibility.

Article Title: {title}
Source: {source}
Content: {content}

Score the article on these dimensions (each 0-10):
1. source_reputation: Is this a known, established outlet?
2. factual_language: Does it use neutral language vs. emotional/sensational language?
3. evidence_quality: Does it cite sources, experts, data?
4. balance: Does it present multiple perspectives?
5. logical_consistency: Are claims internally consistent and logical?

Also classify it as one of:
- "credible": likely accurate, well-sourced
- "mixed": has some good reporting but notable issues
- "misleading": framing distorts facts
- "misinformation": contains factually false claims

Return ONLY a valid JSON object with no markdown, no code fences, no explanation — just the raw JSON:
{{
  "scores": {{
    "source_reputation": 8,
    "factual_language": 7,
    "evidence_quality": 6,
    "balance": 5,
    "logical_consistency": 8
  }},
  "overall_score": 6.8,
  "classification": "mixed",
  "reasoning": "Brief 2-3 sentence explanation of why",
  "red_flags": ["list", "of", "concerns"],
  "strengths": ["list", "of", "positives"]
}}
"""

def score_article(article: dict) -> dict:
    # Guard against missing content before hitting the API
    if not article.get("content") or len(article.get("content", "")) < 50:
        logger.warning(f"Skipping '{article.get('title')}' — insufficient content")
        return _fallback(article, reason="Insufficient content to score")

    prompt = SCORING_PROMPT.format(
        title=article.get("title", "Unknown"),
        source=article.get("source", "Unknown"),
        content=article.get("content", "")
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if present (```json ... ```)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        scored = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse failed for '{article.get('title')}': {e}\nRaw: {raw[:300]}")
        return _fallback(article, reason="LLM returned malformed JSON")

    # Validate expected keys are present
    if "overall_score" not in scored or "classification" not in scored:
        logger.warning(f"Missing keys in scorer response for '{article.get('title')}'")
        return _fallback(article, reason="Incomplete scorer response")

    return {**article, **scored}


def _fallback(article: dict, reason: str) -> dict:
    """Return a safe default when scoring fails so the pipeline keeps running."""
    return {
        **article,
        "overall_score": 0,
        "classification": "unscored",
        "reasoning": reason,
        "red_flags": [],
        "strengths": []
    }