import { useState } from "react";
import { API_BASE_URL } from "../constants";
import { Article, Category } from "../types";

interface UseAnalyzeReturn {
  articles: Article[];
  singleResult: Article | null;
  loading: boolean;
  error: string | null;
  analyze: (keyword: string, category?: Category, numArticles?: number) => Promise<void>;
  analyzeUrl: (url: string) => Promise<void>;
  reset: () => void;
}

export function useAnalyze(): UseAnalyzeReturn {
  const [articles, setArticles] = useState<Article[]>([]);
  const [singleResult, setSingleResult] = useState<Article | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (
    keyword: string,
    category?: Category,
    numArticles: number = 8
  ) => {
    setLoading(true);
    setError(null);
    setArticles([]);
    setSingleResult(null);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 120000); // 2 minutes until timeout.

    try {
      const params = new URLSearchParams({ num_articles: String(numArticles) });
      if (category) params.append('category', category);
      const res = await fetch(
        `${API_BASE_URL}/analyze/${encodeURIComponent(keyword)}?${params}`,
        { signal: controller.signal }
      );
      clearTimeout(timeout);
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setArticles(data.articles);
    } catch (e: any) {
      clearTimeout(timeout);
      setError(e.name === 'AbortError' ? 'Request timed out.' : e.message ?? 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const analyzeUrl = async (url: string) => {
    setLoading(true);
    setError(null);
    setSingleResult(null);
    setArticles([]);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);

    try {
      const res = await fetch(`${API_BASE_URL}/analyze/url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
        signal: controller.signal,
      });
      clearTimeout(timeout);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? `Server error: ${res.status}`);
      }
      const data: Article = await res.json();
      setSingleResult(data);
    } catch (e: any) {
      clearTimeout(timeout);
      setError(e.name === 'AbortError' ? 'Request timed out.' : e.message ?? 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setArticles([]);
    setSingleResult(null);
    setError(null);
  };

  return { articles, singleResult, loading, error, analyze, analyzeUrl, reset };
}