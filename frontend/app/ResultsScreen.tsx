import { RouteProp } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useEffect, useState } from "react";
import {
    FlatList,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from "react-native";
import { RootStackParamList } from "../App";
import { useAnalyze } from "../hooks/useAnalyze";
import { ArticleCard } from "../components/ArticleCard";
import { LoadingScreen } from "../components/LoadingScreen";
import { COLORS, FONTS } from "../constants";

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, "Results">;
  route: RouteProp<RootStackParamList, "Results">;
};

export function ResultsScreen({ navigation, route }: Props) {
  const { keyword, category, numArticles } = route.params;
  const { articles, loading, error, analyze } = useAnalyze();
  const [searchText, setSearchText] = useState("");

  useEffect(() => {
    analyze(keyword, category, numArticles);
  }, []);

  const filtered = searchText.trim()
    ? articles.filter(
        (a) =>
          a.title?.toLowerCase().includes(searchText.toLowerCase()) ||
          a.source?.toLowerCase().includes(searchText.toLowerCase()),
      )
    : articles;

  if (loading) return <LoadingScreen keyword={keyword} />;

  return (
    <View style={styles.root}>
      {/* Top bar */}
      <View style={styles.topBar}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.wordmark}>VERITAS</Text>
        <TouchableOpacity
          onPress={() => navigation.navigate("Home")}
          style={styles.searchIconButton}
        >
          <Text style={styles.backText}>Search</Text>
        </TouchableOpacity>
      </View>

      {/* Query summary */}
      <View style={styles.querySummary}>
        <Text style={styles.queryLabel}>RESULTS FOR</Text>
        <Text style={styles.queryKeyword}>"{keyword}"</Text>
        {error && <Text style={styles.error}>{error}</Text>}
        {!error && !loading && (
          <Text style={styles.queryMeta}>
            {articles.length} article{articles.length !== 1 ? "s" : ""} analyzed
            {category ? ` · ${category}` : ""}
          </Text>
        )}
      </View>

      {/* Filter bar */}
      {articles.length > 3 && (
        <View style={styles.filterBar}>
          <TextInput
            style={styles.filterInput}
            placeholder="Filter by title or source..."
            placeholderTextColor={COLORS.textTertiary}
            value={searchText}
            onChangeText={setSearchText}
            autoCapitalize="none"
            autoCorrect={false}
          />
        </View>
      )}

      <View style={styles.hairline} />

      {/* Article list */}
      <FlatList
        data={filtered}
        keyExtractor={(_, i) => String(i)}
        renderItem={({ item, index }) => (
          <ArticleCard article={item} index={index} />
        )}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          error ? null : <Text style={styles.empty}>No results found.</Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  topBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 56,
    paddingBottom: 12,
  },
  wordmark: {
    fontFamily: FONTS.monoMedium,
    fontSize: 11,
    letterSpacing: 4,
    color: COLORS.text,
  },
  backButton: {
    width: 60,
  },
  searchIconButton: {
    width: 60,
    alignItems: "flex-end",
  },
  backText: {
    fontFamily: FONTS.mono,
    fontSize: 12,
    color: COLORS.textSecondary,
    letterSpacing: 0.3,
  },
  querySummary: {
    paddingHorizontal: 20,
    paddingBottom: 14,
  },
  queryLabel: {
    fontFamily: FONTS.monoMedium,
    fontSize: 9,
    letterSpacing: 1.5,
    color: COLORS.textTertiary,
    marginBottom: 4,
  },
  queryKeyword: {
    fontFamily: FONTS.serif,
    fontSize: 22,
    color: COLORS.text,
    marginBottom: 4,
  },
  queryMeta: {
    fontFamily: FONTS.mono,
    fontSize: 10,
    color: COLORS.textTertiary,
    letterSpacing: 0.3,
  },
  filterBar: {
    paddingHorizontal: 20,
    paddingBottom: 10,
  },
  filterInput: {
    fontFamily: FONTS.mono,
    fontSize: 12,
    color: COLORS.text,
    backgroundColor: COLORS.accentLight,
    borderRadius: 4,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  hairline: {
    height: 1,
    backgroundColor: COLORS.border,
    marginBottom: 12,
  },
  list: {
    paddingHorizontal: 16,
    paddingBottom: 40,
  },
  empty: {
    fontFamily: FONTS.serif,
    fontSize: 16,
    color: COLORS.textTertiary,
    textAlign: "center",
    marginTop: 60,
  },
  error: {
    fontFamily: FONTS.mono,
    fontSize: 11,
    color: COLORS.danger,
    marginTop: 4,
  },
});
