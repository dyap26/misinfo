import anthropic
import json
import logging
import os
import re
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env.local")

logger = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SCORING_PROMPT = """
You are a media literacy and fact-checking expert with deep knowledge of journalistic standards.

Analyze the following news article and evaluate its factual credibility across multiple dimensions.

Article Title: {title}
Source: {source}
Content: {content}

---

SCORING INSTRUCTIONS

Score each dimension from 0 to 10 using these anchors:
  0–2 = Very poor / major failure
  3–4 = Below average / significant issues
  5–6 = Average / some issues present
  7–8 = Good / minor issues only
  9–10 = Excellent / meets highest standards

DIMENSIONS:

1. source_reputation (0–10)
   Does this outlet have a track record of accuracy? Is it an established, known publication?
   Consider: editorial standards, history of corrections, known bias or funding sources.

2. evidence_quality (0–10)
   Are claims supported by named sources, experts, data, or documents?
   Consider: use of primary vs. secondary sources, vague attribution ("sources say"), expert credentials.

3. factual_language (0–10)
   Does the article use neutral, precise language rather than emotional or sensational framing?
   Consider: loaded words, exaggeration, conflation of opinion with fact, misleading headlines.

4. balance (0–10)
   Does the article represent multiple credible perspectives where relevant?
   Consider: missing voices, strawman representation of opposing views, one-sidedness on contested topics.

5. logical_consistency (0–10)
   Are the claims internally consistent and logically sound?
   Consider: internal contradictions, headline vs. body mismatches, correlation/causation conflation.

6. verifiability (0–10)
   Can the article's specific claims be checked against external sources?
   Consider: named sources, cited studies, specific dates/figures, links to original data.

7. context_and_framing (0–10)
   Is sufficient context provided to understand the story accurately?
   Consider: missing historical context, deceptive framing, selective use of statistics, out-of-context quotes.

---

CLASSIFICATION

Classify the article as exactly one of:
- "credible": Well-sourced, factually sound, minimal issues
- "mixed": Some quality reporting but notable factual or framing issues
- "misleading": Framing or omissions materially distort the factual picture
- "misinformation": Contains claims that are demonstrably false

---

OVERALL SCORE

Compute overall_score as a weighted average:
  evidence_quality:       22%
  verifiability:          18%
  factual_language:       15%
  logical_consistency:    15%
  context_and_framing:    15%
  balance:                10%
  source_reputation:       5%

Round to one decimal place.

---

OUTPUT FORMAT

Return ONLY a valid JSON object. No markdown, no code fences, no explanation outside the JSON.

{
  "scores": {
    "source_reputation": 0,
    "evidence_quality": 0,
    "factual_language": 0,
    "balance": 0,
    "logical_consistency": 0,
    "verifiability": 0,
    "context_and_framing": 0
  },
  "overall_score": 0.0,
  "classification": "credible" | "mixed" | "misleading" | "misinformation",
  "reasoning": "2–3 sentences explaining the overall assessment and classification.",
  "red_flags": ["specific concern 1", "specific concern 2"],
  "strengths": ["specific strength 1", "specific strength 2"]
}
"""

WEIGHTS = {
    "evidence_quality": 0.22,
    "verifiability": 0.18,
    "factual_language": 0.15,
    "logical_consistency": 0.15,
    "context_and_framing": 0.15,
    "balance": 0.10,
    "source_reputation": 0.05,
}


def _strip_fences(text: str) -> str:
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    return match.group(1).strip() if match else text.strip()


def _validate_scores(scores: dict) -> dict:
    return {k: max(0, min(10, v)) for k, v in scores.items()}


def _compute_score(scores: dict) -> float:
    return round(sum(scores.get(k, 0) * w for k, w in WEIGHTS.items()), 1)


def _fallback(article: dict, reason: str) -> dict:
    return {
        **article,
        "scores": {},
        "overall_score": 0,
        "classification": "unscored",
        "reasoning": reason,
        "red_flags": [],
        "strengths": [],
    }


def score_article(article: dict) -> dict:
    if not article.get("content") or len(article.get("content", "")) < 50:
        logger.warning(f"Skipping '{article.get('title')}' — insufficient content")
        return _fallback(article, reason="Insufficient content to score")

    prompt = (SCORING_PROMPT
        .replace("{title}", article.get("title", "Unknown"))
        .replace("{source}", article.get("source", "Unknown"))
        .replace("{content}", article.get("content", ""))
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        if response.stop_reason == "max_tokens":
          logger.warning(f"Response truncated for '{article.get('title')}' — increase max_tokens")
          return _fallback(article, reason="Response truncated by max_tokens limit")
    except anthropic.APIError as e:
        logger.error(f"API error for '{article.get('title')}': {e}")
        return _fallback(article, reason=f"API error: {e}")

    raw = _strip_fences(response.content[0].text)
    logger.debug(f"Raw response for '{article.get('title')}':\n{raw[:500]}")

    try:
        scored = json.loads(raw)
    except json.JSONDecodeError as e:
      logger.warning(f"JSON parse failed for '{article.get('title')}': {e}\nFull raw:\n{raw}")
      return _fallback(article, reason="LLM returned malformed JSON")

    if "scores" not in scored or "classification" not in scored:
        logger.warning(f"Missing keys in scorer response for '{article.get('title')}'")
        return _fallback(article, reason="Incomplete scorer response")

    scored["scores"] = _validate_scores(scored["scores"])
    scored["overall_score"] = _compute_score(scored["scores"])

    return {**article, **scored}