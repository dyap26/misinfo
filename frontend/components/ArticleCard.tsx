import React, { useRef, useState } from "react";
import {
    Animated,
    LayoutAnimation,
    Linking,
    Platform,
    StyleSheet,
    Text,
    TouchableOpacity,
    UIManager,
    View,
} from "react-native";
import { COLORS, FONTS } from "../constants";
import { Article } from "../types";
import { ClassificationBadge } from "./ClassificationBadge";
import { ScoreRing } from "./ScoreRing";

if (Platform.OS === "android") {
  UIManager.setLayoutAnimationEnabledExperimental?.(true);
}

interface ArticleCardProps {
  article: Article;
  index: number;
}

export function ArticleCard({ article, index }: ArticleCardProps) {
  const [expanded, setExpanded] = useState(false);
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(16)).current;

  React.useEffect(() => {
    Animated.parallel([
      Animated.timing(opacity, {
        toValue: 1,
        duration: 400,
        delay: index * 80,
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: 0,
        duration: 400,
        delay: index * 80,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const toggle = () => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpanded((v) => !v);
  };

  const openUrl = () => {
    if (article.url) Linking.openURL(article.url);
  };

  return (
    <Animated.View
      style={[styles.card, { opacity, transform: [{ translateY }] }]}
    >
      <TouchableOpacity onPress={toggle} activeOpacity={0.85}>
        {/* Header row */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <ClassificationBadge classification={article.classification} />
            <Text style={styles.source} numberOfLines={1}>
              {article.source}
            </Text>
          </View>
          <ScoreRing score={article.overall_score} />
        </View>

        {/* Title */}
        <Text style={styles.title} numberOfLines={expanded ? undefined : 2}>
          {article.title}
        </Text>

        {/* Chevron */}
        <View style={styles.chevronRow}>
          <Text style={styles.expandHint}>
            {expanded ? "Collapse" : "Show analysis"}
          </Text>
          <Text style={styles.chevron}>{expanded ? "↑" : "↓"}</Text>
        </View>
      </TouchableOpacity>

      {/* Expanded content */}
      {expanded && (
        <View style={styles.expandedContent}>
          <View style={styles.divider} />

          {/* Reasoning */}
          <Text style={styles.sectionLabel}>ASSESSMENT</Text>
          <Text style={styles.reasoning}>{article.reasoning}</Text>

          {/* Red Flags */}
          {article.red_flags?.length > 0 && (
            <View style={styles.section}>
              <Text style={[styles.sectionLabel, { color: "#8a3a00" }]}>
                ⚠ RED FLAGS
              </Text>
              {article.red_flags.map((flag, i) => (
                <View key={i} style={styles.bulletRow}>
                  <Text style={[styles.bullet, { color: "#8a3a00" }]}>—</Text>
                  <Text style={styles.bulletText}>{flag}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Strengths */}
          {article.strengths?.length > 0 && (
            <View style={styles.section}>
              <Text style={[styles.sectionLabel, { color: COLORS.success }]}>
                ✓ STRENGTHS
              </Text>
              {article.strengths.map((s, i) => (
                <View key={i} style={styles.bulletRow}>
                  <Text style={[styles.bullet, { color: COLORS.success }]}>
                    —
                  </Text>
                  <Text style={styles.bulletText}>{s}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Score breakdown */}
          {article.scores && Object.keys(article.scores).length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionLabel}>SCORE BREAKDOWN</Text>
              {Object.entries(article.scores).map(([key, val]) => (
                <View key={key} style={styles.scoreRow}>
                  <Text style={styles.scoreKey}>{key.replace(/_/g, " ")}</Text>
                  <View style={styles.scoreBarBg}>
                    <View
                      style={[
                        styles.scoreBarFill,
                        { width: `${(val / 10) * 100}%` },
                      ]}
                    />
                  </View>
                  <Text style={styles.scoreVal}>{val}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Link */}
          {article.url ? (
            <TouchableOpacity onPress={openUrl} style={styles.linkButton}>
              <Text style={styles.linkText}>Read article →</Text>
            </TouchableOpacity>
          ) : null}
        </View>
      )}
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
    padding: 16,
    marginBottom: 10,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 8,
  },
  headerLeft: {
    flex: 1,
    marginRight: 12,
    gap: 5,
  },
  source: {
    fontFamily: FONTS.mono,
    fontSize: 11,
    color: COLORS.textSecondary,
    letterSpacing: 0.2,
  },
  title: {
    fontFamily: FONTS.serifRegular,
    fontSize: 16,
    color: COLORS.text,
    lineHeight: 22,
    marginBottom: 10,
  },
  chevronRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  expandHint: {
    fontFamily: FONTS.mono,
    fontSize: 10,
    color: COLORS.textTertiary,
    letterSpacing: 0.4,
  },
  chevron: {
    fontFamily: FONTS.mono,
    fontSize: 11,
    color: COLORS.textTertiary,
  },
  divider: {
    height: 1,
    backgroundColor: COLORS.border,
    marginVertical: 14,
  },
  expandedContent: {},
  sectionLabel: {
    fontFamily: FONTS.monoMedium,
    fontSize: 9,
    letterSpacing: 1,
    color: COLORS.textTertiary,
    marginBottom: 6,
  },
  reasoning: {
    fontFamily: FONTS.sans,
    fontSize: 13,
    color: COLORS.textSecondary,
    lineHeight: 19,
    marginBottom: 14,
  },
  section: {
    marginBottom: 14,
  },
  bulletRow: {
    flexDirection: "row",
    gap: 6,
    marginBottom: 3,
  },
  bullet: {
    fontFamily: FONTS.mono,
    fontSize: 12,
    lineHeight: 18,
  },
  bulletText: {
    fontFamily: FONTS.sans,
    fontSize: 12,
    color: COLORS.textSecondary,
    lineHeight: 18,
    flex: 1,
  },
  scoreRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 5,
    gap: 8,
  },
  scoreKey: {
    fontFamily: FONTS.mono,
    fontSize: 9,
    color: COLORS.textTertiary,
    width: 110,
    textTransform: "capitalize",
  },
  scoreBarBg: {
    flex: 1,
    height: 3,
    backgroundColor: COLORS.border,
    borderRadius: 2,
    overflow: "hidden",
  },
  scoreBarFill: {
    height: "100%",
    backgroundColor: COLORS.text,
    borderRadius: 2,
  },
  scoreVal: {
    fontFamily: FONTS.mono,
    fontSize: 10,
    color: COLORS.textSecondary,
    width: 16,
    textAlign: "right",
  },
  linkButton: {
    marginTop: 4,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  linkText: {
    fontFamily: FONTS.monoMedium,
    fontSize: 11,
    color: COLORS.text,
    letterSpacing: 0.3,
  },
});
