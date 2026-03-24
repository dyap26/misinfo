import React, { useEffect, useRef } from "react";
import { Animated, StyleSheet, Text, View } from "react-native";
import { COLORS, FONTS } from "../constants";

const STEPS = [
  "Fetching articles",
  "Scraping content",
  "Running analysis",
  "Scoring credibility",
];

export function LoadingScreen({ keyword }: { keyword: string }) {
  const dots = useRef(new Animated.Value(0)).current;
  const [stepIndex, setStepIndex] = React.useState(0);
  const barWidth = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Animate progress bar
    Animated.timing(barWidth, {
      toValue: 1,
      duration: 8000,
      useNativeDriver: false,
    }).start();

    // Cycle through steps
    const interval = setInterval(() => {
      setStepIndex((i) => Math.min(i + 1, STEPS.length - 1));
    }, 2000);

    // Pulse dots
    Animated.loop(
      Animated.sequence([
        Animated.timing(dots, {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
        }),
        Animated.timing(dots, {
          toValue: 0,
          duration: 600,
          useNativeDriver: true,
        }),
      ]),
    ).start();

    return () => clearInterval(interval);
  }, []);

  return (
    <View style={styles.container}>
      <View style={styles.inner}>
        <Text style={styles.wordmark}>VERITAS</Text>
        <Text style={styles.analyzing}>Analyzing</Text>
        <Text style={styles.keyword}>"{keyword}"</Text>

        <View style={styles.progressBg}>
          <Animated.View
            style={[
              styles.progressFill,
              {
                width: barWidth.interpolate({
                  inputRange: [0, 1],
                  outputRange: ["0%", "100%"],
                }),
              },
            ]}
          />
        </View>

        <View style={styles.stepRow}>
          {STEPS.map((step, i) => (
            <Text
              key={step}
              style={[styles.step, i === stepIndex && styles.stepActive]}
            >
              {i < stepIndex ? "✓ " : i === stepIndex ? "→ " : "  "}
              {step}
            </Text>
          ))}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    justifyContent: "center",
    alignItems: "center",
  },
  inner: {
    width: "80%",
    alignItems: "center",
  },
  wordmark: {
    fontFamily: FONTS.monoMedium,
    fontSize: 11,
    letterSpacing: 4,
    color: COLORS.textTertiary,
    marginBottom: 40,
  },
  analyzing: {
    fontFamily: FONTS.serif,
    fontSize: 13,
    color: COLORS.textTertiary,
    marginBottom: 6,
    letterSpacing: 0.5,
  },
  keyword: {
    fontFamily: FONTS.serif,
    fontSize: 26,
    color: COLORS.text,
    marginBottom: 36,
    textAlign: "center",
  },
  progressBg: {
    width: "100%",
    height: 1,
    backgroundColor: COLORS.border,
    marginBottom: 28,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: COLORS.text,
  },
  stepRow: {
    width: "100%",
    gap: 8,
  },
  step: {
    fontFamily: FONTS.mono,
    fontSize: 11,
    color: COLORS.textTertiary,
    letterSpacing: 0.3,
  },
  stepActive: {
    color: COLORS.text,
  },
});
