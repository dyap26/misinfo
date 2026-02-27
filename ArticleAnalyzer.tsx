import React, { useState } from 'react';
import {
  View,
  TextInput,
  FlatList,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
  ListRenderItem,
} from 'react-native';

const CREDIBILITY_COLORS = {
  credible: '#22c55e',
  mixed: '#f59e0b',
  misleading: '#f97316',
  misinformation: '#ef4444',
};

type CredibilityClassification = keyof typeof CREDIBILITY_COLORS;

type Article = {
  title: string;
  source: string;
  classification: CredibilityClassification;
  overall_score?: number;
  reasoning: string;
  red_flags?: string[];
};

function ArticleAnalyzer() {
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    setLoading(true);
    try {
      // TODO: Change later to use API
      const res = await fetch(`https://your-api.com/analyze/${keyword}?num_articles=10`);
      const data = await res.json();
      setResults(data.articles as Article[]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const renderArticle: ListRenderItem<Article> = ({ item }) => (
    <View style={styles.card}>
      <View style={[styles.badge, { backgroundColor: CREDIBILITY_COLORS[item.classification] }]}>
        <Text style={styles.badgeText}>{item.classification.toUpperCase()}</Text>
      </View>
      <Text style={styles.title}>{item.title}</Text>
      <Text style={styles.source}>
        {item.source} · {item.overall_score?.toFixed(1)}/10
      </Text>
      <Text style={styles.reasoning}>{item.reasoning}</Text>
      {item.red_flags?.length ? (
        <Text style={styles.redFlags}>⚠️ {item.red_flags.join(' · ')}</Text>
      ) : null}
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.searchRow}>
        <TextInput
          style={styles.input}
          placeholder="Enter keyword (e.g. tariff)"
          value={keyword}
          onChangeText={setKeyword}
        />
        <TouchableOpacity style={styles.button} onPress={analyze}>
          <Text style={styles.buttonText}>Analyze</Text>
        </TouchableOpacity>
      </View>
      {loading ? (
        <ActivityIndicator size="large" />
      ) : (
        <FlatList data={results} renderItem={renderArticle} keyExtractor={(_, i) => i.toString()} />
      )}
    </View>
  );
}

export default ArticleAnalyzer;

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#f8fafc' },
  searchRow: { flexDirection: 'row', marginBottom: 12 },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    borderRadius: 8,
    padding: 10,
    backgroundColor: '#fff',
  },
  button: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    padding: 10,
    justifyContent: 'center',
    marginLeft: 8,
  },
  buttonText: { color: '#fff', fontWeight: 'bold' },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  badge: {
    alignSelf: 'flex-start',
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginBottom: 6,
  },
  badgeText: { color: '#fff', fontSize: 11, fontWeight: 'bold' },
  title: { fontSize: 15, fontWeight: '600', marginBottom: 4 },
  source: { fontSize: 12, color: '#64748b', marginBottom: 6 },
  reasoning: { fontSize: 13, color: '#374151', marginBottom: 6 },
  redFlags: { fontSize: 12, color: '#ef4444' },
});

