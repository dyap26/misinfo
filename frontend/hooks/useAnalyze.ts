import { useState } from "react";
import { usePostHog } from "posthog-react-native";
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
  const posthog = usePostHog();
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
      posthog.capture('analysis_completed', {
        keyword,
        category: category ?? null,
        num_articles_requested: numArticles,
        num_articles_returned: data.articles?.length ?? 0,
      });
    } catch (e: any) {
      clearTimeout(timeout);
      const isTimeout = e.name === 'AbortError';
      const message = isTimeout ? 'Request timed out.' : e.message ?? 'Something went wrong.';
      setError(message);
      posthog.capture('analysis_failed', {
        keyword,
        category: category ?? null,
        is_timeout: isTimeout,
        error_message: message,
      });
      if (!isTimeout) {
        posthog.capture('$exception', {
          $exception_list: [
            {
              type: e.name ?? 'Error',
              value: message,
              stacktrace: { type: 'raw', frames: e.stack ?? '' },
            },
          ],
          $exception_source: 'useAnalyze.analyze',
        });
      }
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
      posthog.capture('url_analysis_completed', {
        classification: data.classification,
        overall_score: data.overall_score,
        source: data.source,
      });
    } catch (e: any) {
      clearTimeout(timeout);
      const isTimeout = e.name === 'AbortError';
      const message = isTimeout ? 'Request timed out.' : e.message ?? 'Something went wrong.';
      setError(message);
      posthog.capture('analysis_failed', {
        search_type: 'url',
        is_timeout: isTimeout,
        error_message: message,
      });
      if (!isTimeout) {
        posthog.capture('$exception', {
          $exception_list: [
            {
              type: e.name ?? 'Error',
              value: message,
              stacktrace: { type: 'raw', frames: e.stack ?? '' },
            },
          ],
          $exception_source: 'useAnalyze.analyzeUrl',
        });
      }
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