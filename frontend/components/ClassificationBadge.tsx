import { StyleSheet, Text, View } from "react-native";
import { CLASSIFICATION_CONFIG, FONTS } from "../constants";
import { Classification } from "../types";

interface ClassificationBadgeProps {
  classification: Classification;
  small?: boolean;
}

export function ClassificationBadge({
  classification,
  small,
}: ClassificationBadgeProps) {
  const config =
    CLASSIFICATION_CONFIG[classification] ?? CLASSIFICATION_CONFIG.unscored;

  return (
    <View
      style={[
        styles.badge,
        { backgroundColor: config.bg },
        small && styles.small,
      ]}
    >
      <Text
        style={[
          styles.label,
          { color: config.color },
          small && styles.smallLabel,
        ]}
      >
        {config.label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 3,
    alignSelf: "flex-start",
  },
  label: {
    fontFamily: FONTS.monoMedium,
    fontSize: 10,
    letterSpacing: 0.8,
  },
  small: {
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  smallLabel: {
    fontSize: 9,
  },
});
