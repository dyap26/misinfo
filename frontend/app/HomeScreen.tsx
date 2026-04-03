import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useRef, useState } from "react";
import {
    Animated,
    KeyboardAvoidingView,
    Platform,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from "react-native";
import { RootStackParamList } from "../App";
import { useAnalyze } from "../hooks/useAnalyze";
import { CATEGORIES, COLORS, FONTS } from "../constants";
import { Category } from "../types";

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, "Home">;
};

export function HomeScreen({ navigation }: Props) {
  const [keyword, setKeyword] = useState("");
  const [category, setCategory] = useState<Category | undefined>(undefined);
  const [numArticles, setNumArticles] = useState(5);
  const { analyze, loading, error } = useAnalyze();
  const inputRef = useRef<TextInput>(null);
  const underlineWidth = useRef(new Animated.Value(0)).current;

  const onFocus = () => {
    Animated.timing(underlineWidth, {
      toValue: 1,
      duration: 250,
      useNativeDriver: false,
    }).start();
  };
  const onBlur = () => {
    Animated.timing(underlineWidth, {
      toValue: 0,
      duration: 200,
      useNativeDriver: false,
    }).start();
  };

  const handleSearch = async () => {
    if (!keyword.trim()) return;
    navigation.navigate("Results", {
      keyword: keyword.trim(),
      category,
      numArticles,
    });
  };

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled"
      >
        {/* Wordmark */}
        <View style={styles.header}>
          <Text style={styles.wordmark}>VERITAS</Text>
          <Text style={styles.tagline}>News credibility analysis</Text>
        </View>

        {/* Divider */}
        <View style={styles.hairline} />

        {/* Search input */}
        <View style={styles.inputSection}>
          <Text style={styles.fieldLabel}>KEYWORD</Text>
          <TouchableOpacity
            onPress={() => inputRef.current?.focus()}
            activeOpacity={1}
          >
            <TextInput
              ref={inputRef}
              style={styles.input}
              value={keyword}
              onChangeText={setKeyword}
              placeholder="e.g. climate change, AI regulation..."
              placeholderTextColor={COLORS.textTertiary}
              returnKeyType="search"
              onSubmitEditing={handleSearch}
              onFocus={onFocus}
              onBlur={onBlur}
              autoCapitalize="none"
              autoCorrect={false}
            />
            <Animated.View
              style={[
                styles.inputUnderline,
                {
                  width: underlineWidth.interpolate({
                    inputRange: [0, 1],
                    outputRange: ["0%", "100%"],
                  }),
                },
              ]}
            />
            <View style={styles.inputUnderlineBase} />
          </TouchableOpacity>
        </View>

        {/* Category Selection */}
        <View style={styles.fieldSection}>
          <Text style={styles.fieldLabel}>CATEGORY</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.categoryScroll}
          >
            {CATEGORIES.map((cat) => {
              const selected = cat.value === category;
              return (
                <TouchableOpacity
                  key={cat.label}
                  style={[
                    styles.categoryChip,
                    selected && styles.categoryChipSelected,
                  ]}
                  onPress={() => setCategory(cat.value as Category | undefined)}
                  activeOpacity={0.7}
                >
                  <Text
                    style={[
                      styles.categoryLabel,
                      selected && styles.categoryLabelSelected,
                    ]}
                  >
                    {cat.label}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>
        </View>

        {/* Article count */}
        <View style={styles.fieldSection}>
          <Text style={styles.fieldLabel}>ARTICLES TO FETCH</Text>
          <View style={styles.countRow}>
            {[5, 10, 15].map((n) => (
              <TouchableOpacity
                key={n}
                style={[
                  styles.countChip,
                  numArticles === n && styles.countChipSelected,
                ]}
                onPress={() => setNumArticles(n)}
                activeOpacity={0.7}
              >
                <Text
                  style={[
                    styles.countLabel,
                    numArticles === n && styles.countLabelSelected,
                  ]}
                >
                  {n}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {error && <Text style={styles.error}>{error}</Text>}

        {/* Search button */}
        <TouchableOpacity
          style={[
            styles.searchButton,
            !keyword.trim() && styles.searchButtonDisabled,
          ]}
          onPress={handleSearch}
          disabled={!keyword.trim()}
          activeOpacity={0.85}
        >
          <Text style={styles.searchButtonText}>Analyze →</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  container: {
    flexGrow: 1,
    paddingHorizontal: 28,
    paddingTop: 80,
    paddingBottom: 40,
  },
  header: {
    marginBottom: 32,
  },
  wordmark: {
    fontFamily: FONTS.monoMedium,
    fontSize: 13,
    letterSpacing: 5,
    color: COLORS.text,
    marginBottom: 6,
  },
  tagline: {
    fontFamily: FONTS.serifRegular,
    fontSize: 22,
    color: COLORS.textSecondary,
    lineHeight: 28,
  },
  hairline: {
    height: 1,
    backgroundColor: COLORS.border,
    marginBottom: 36,
  },
  inputSection: {
    marginBottom: 30,
  },
  fieldLabel: {
    fontFamily: FONTS.monoMedium,
    fontSize: 9,
    letterSpacing: 1.5,
    color: COLORS.textTertiary,
    marginBottom: 10,
  },
  input: {
    fontFamily: FONTS.serif,
    fontSize: 18,
    color: COLORS.text,
    paddingVertical: 6,
    paddingHorizontal: 0,
  },
  inputUnderlineBase: {
    height: 1,
    backgroundColor: COLORS.border,
  },
  inputUnderline: {
    height: 1,
    backgroundColor: COLORS.text,
    position: "absolute",
    bottom: 0,
    left: 0,
    zIndex: 1,
  },
  fieldSection: {
    marginBottom: 28,
  },
  categoryScroll: {
    marginHorizontal: -4,
  },
  categoryChip: {
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 3,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginHorizontal: 4,
  },
  categoryChipSelected: {
    backgroundColor: COLORS.text,
    borderColor: COLORS.text,
  },
  categoryLabel: {
    fontFamily: FONTS.mono,
    fontSize: 11,
    color: COLORS.textSecondary,
    letterSpacing: 0.3,
  },
  categoryLabelSelected: {
    color: COLORS.surface,
  },
  countRow: {
    flexDirection: "row",
    gap: 8,
  },
  countChip: {
    width: 48,
    height: 36,
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 3,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  countChipSelected: {
    backgroundColor: COLORS.text,
    borderColor: COLORS.text,
  },
  countLabel: {
    fontFamily: FONTS.mono,
    fontSize: 13,
    color: COLORS.textSecondary,
  },
  countLabelSelected: {
    color: COLORS.surface,
  },
  searchButton: {
    backgroundColor: COLORS.text,
    borderRadius: 4,
    paddingVertical: 16,
    alignItems: "center",
    marginTop: 12,
  },
  searchButtonDisabled: {
    backgroundColor: COLORS.borderStrong,
  },
  searchButtonText: {
    fontFamily: FONTS.monoMedium,
    fontSize: 13,
    color: COLORS.surface,
    letterSpacing: 1,
  },
  error: {
    fontFamily: FONTS.mono,
    fontSize: 11,
    color: COLORS.danger,
    marginBottom: 12,
  },
});
