export type Classification = 'credible' | 'mixed' | 'misleading' | 'misinformation' | 'unscored';

export type Category =
  | 'business'
  | 'entertainment'
  | 'general'
  | 'health'
  | 'science'
  | 'sports'
  | 'technology';

export interface ArticleScores {
  source_reputation: number;
  evidence_quality: number;
  factual_language: number;
  balance: number;
  logical_consistency: number;
  verifiability: number;
  context_and_framing: number;
}

export interface Article {
  title: string;
  source: string;
  url: string;
  overall_score: number;
  classification: Classification;
  reasoning: string;
  red_flags: string[];
  strengths: string[];
  scores: ArticleScores;
  scrape_status?: 'ok' | 'paywall' | 'scrape_failed';
}
