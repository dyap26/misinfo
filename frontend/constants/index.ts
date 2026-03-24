import { Classification } from '../types';

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

export const CATEGORIES = [
  { label: 'All', value: undefined },
  { label: 'Business', value: 'business' },
  { label: 'Entertainment', value: 'entertainment' },
  { label: 'General', value: 'general' },
  { label: 'Health', value: 'health' },
  { label: 'Science', value: 'science' },
  { label: 'Sports', value: 'sports' },
  { label: 'Technology', value: 'technology' },
] as const;

export const CLASSIFICATION_CONFIG: Record<
  Classification,
  { label: string; color: string; bg: string }
> = {
  credible: {
    label: 'CREDIBLE',
    color: '#1a6640',
    bg: '#edf7f1',
  },
  mixed: {
    label: 'MIXED',
    color: '#7a5c00',
    bg: '#fdf8e7',
  },
  misleading: {
    label: 'MISLEADING',
    color: '#8a3a00',
    bg: '#fdf2ec',
  },
  misinformation: {
    label: 'MISINFORMATION',
    color: '#7a1a1a',
    bg: '#fdf0f0',
  },
  unscored: {
    label: 'UNSCORED',
    color: '#888',
    bg: '#f5f5f5',
  },
};

export const COLORS = {
  background: '#fafaf8',
  surface: '#ffffff',
  border: '#e8e8e4',
  borderStrong: '#d0d0c8',
  text: '#1a1a18',
  textSecondary: '#6b6b65',
  textTertiary: '#9b9b93',
  accent: '#1a1a18',
  accentLight: '#f0f0ec',
  danger: '#c0392b',
  success: '#1a6640',
  warning: '#7a5c00',
};

export const FONTS = {
  serif: 'PlayfairDisplay_700Bold',
  serifRegular: 'PlayfairDisplay_400Regular',
  mono: 'JetBrainsMono_400Regular',
  monoMedium: 'JetBrainsMono_500Medium',
  sans: 'DMSans_400Regular',
  sansMedium: 'DMSans_500Medium',
  sansBold: 'DMSans_700Bold',
};
