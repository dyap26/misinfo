import anthropic
import json

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Prompt for scoring the article using Claude
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

Return ONLY a JSON object like this:
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

# Score the article
def score_article(article: dict) -> dict:
    prompt = SCORING_PROMPT.format(
        title=article["title"],
        source=article["source"],
        content=article["content"]
    )
    
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw = response.content[0].text
    scored = json.loads(raw)
    return {**article, **scored}