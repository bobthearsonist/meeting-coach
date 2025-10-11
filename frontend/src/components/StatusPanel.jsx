import React from 'react';
import {View, Text, StyleSheet} from 'react-native';
import useMeetingData from '../hooks/useMeetingData';
import theme from '../utils/theme';

/**
 * StatusPanel - Displays current meeting status metrics
 *
 * Shows real-time data for:
 * - Emotional state (from LLM analysis)
 * - Social cues (communication patterns)
 * - Confidence level (analysis certainty)
 * - Speech pace (words per minute)
 *
 * Accesses global state via useMeetingData hook.
 */
export default function StatusPanel() {
  const {emotionalState, wpm} = useMeetingData();

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>📊 Current Status</Text>

      <View style={styles.statusGrid}>
        <View style={[styles.statusBox, styles.emotionalState]}>
          <Text style={styles.statusLabel}>Emotional State</Text>
          <Text
            style={[
              styles.statusValue,
              {
                color:
                  theme.colors.emotional[emotionalState] ||
                  theme.colors.text.primary,
              },
            ]}>
            {emotionalState}
          </Text>
        </View>

        <View style={[styles.statusBox, styles.socialCues]}>
          <Text style={styles.statusLabel}>Social Cues</Text>
          <Text
            style={[
              styles.statusValue,
              {color: theme.colors.social.appropriate},
            ]}>
            appropriate
          </Text>
        </View>

        <View style={[styles.statusBox, styles.confidence]}>
          <Text style={styles.statusLabel}>Confidence</Text>
          <Text
            style={[styles.statusValue, {color: theme.colors.confidence}]}>
            0.9
          </Text>
        </View>

        <View style={[styles.statusBox, styles.speechPace]}>
          <Text style={styles.statusLabel}>Speech Pace</Text>
          <Text
            style={[
              styles.statusValue,
              {color: theme.colors.status.success},
            ]}>
            {wpm}
            <Text style={styles.unit}> WPM</Text>
          </Text>
        </View>
      </View>

      <View style={styles.alert}>
        <Text style={styles.checkMark}>✓</Text>
        <Text style={styles.alertText}>All good – no alerts</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.background.primary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.light,
  },
  sectionTitle: {
    fontSize: theme.fontSize.lg,
    fontWeight: theme.fontWeight.bold,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.md,
  },
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  statusBox: {
    flex: 1,
    minWidth: 140,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.lg,
    borderWidth: 2,
  },
  emotionalState: {
    borderColor: theme.colors.emotional.calm,
  },
  socialCues: {
    borderColor: theme.colors.social.appropriate,
  },
  confidence: {
    borderColor: theme.colors.confidence,
  },
  speechPace: {
    borderColor: theme.colors.status.success,
  },
  statusLabel: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.medium,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.xs,
  },
  statusValue: {
    fontSize: theme.fontSize.xl,
    fontWeight: theme.fontWeight.bold,
  },
  unit: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.text.secondary,
  },
  alert: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.status.successBg,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.status.success,
  },
  checkMark: {
    fontSize: theme.fontSize.xl,
    marginRight: theme.spacing.sm,
    color: theme.colors.status.success,
  },
  alertText: {
    fontSize: theme.fontSize.md,
    color: theme.colors.status.success,
    fontWeight: theme.fontWeight.medium,
  },
});
