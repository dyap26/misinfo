import { useState } from "react";
import { API_BASE_URL } from "../constants";
import { Article, Category } from "../types";

interface UseAnalyzeReturn {
  articles: Article[];
  loading: boolean;
  error: string | null;
  analyze: (
    keyword: string,
    category?: Category,
    numArticles?: number,
  ) => Promise<void>;
  reset: () => void;
}

export function useAnalyze(): UseAnalyzeReturn {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (
    keyword: string,
    category?: Category,
    numArticles: number = 8,
  ) => {
    console.log('API_BASE_URL:', API_BASE_URL);
    setLoading(true);
    setError(null);
    setArticles([]);

    try {
      const params = new URLSearchParams({ num_articles: String(numArticles) });
      if (category) params.append("category", category);
      const res = await fetch(
        `${API_BASE_URL}/analyze/${encodeURIComponent(keyword)}?${params}`,
      );
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      const articles: Article[] = data.articles;
      setArticles(articles);
    } catch (e: any) {
      setError(e.message ?? "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setArticles([]);
    setError(null);
  };

  return { articles, loading, error, analyze, reset };
}
