import React from 'react';
import {View, Text, StyleSheet} from 'react-native';
import useMeetingData from '../hooks/useMeetingData';
import theme, {commonStyles} from '../utils/theme';

/**
 * EmotionalTimeline - Displays emotional state timeline visualization
 *
 * Shows:
 * - Timeline header with title and time range
 * - Dominant emotional state (most common state over period)
 * - Time range for the analysis
 * - Visual timeline bar with color-coded segments representing emotional states
 *
 * LEARNING: This component visualizes emotional state changes over time.
 * The timeline bar uses flex properties to show relative duration of each state.
 * Future enhancement: Wire to real timeline data from backend.
 *
 * Accesses global state via useMeetingData hook.
 */
export default function EmotionalTimeline() {
  const {emotionalState} = useMeetingData();

  return (
    <View style={styles.container}>
      <View style={styles.timelineHeader}>
        <Text style={styles.sectionTitle}>📈 Emotional Timeline</Text>
        <Text style={styles.timeText}>Last 5 minutes</Text>
      </View>

      <View style={styles.timelineContent}>
        <View style={styles.dominant}>
          <Text style={styles.dominantLabel}>
            Dominant:{' '}
            <Text style={styles.dominantValue}>🧘 CALM (0.9)</Text>
          </Text>
        </View>
        <Text style={styles.range}>Range: 17:19 – 17:21</Text>

        <View style={styles.timelineBar}>
          <View style={styles.timelineSegment1} />
          <View style={styles.timelineSegment2} />
          <View style={styles.timelineSegment3} />
          <View style={styles.timelineSegment4} />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    ...commonStyles.section,
  },
  sectionTitle: {
    fontSize: theme.fontSize.lg,
    fontWeight: theme.fontWeight.bold,
    color: theme.colors.text.primary,
  },
  timelineHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.lg,
  },
  timeText: {
    color: theme.colors.text.secondary,
    fontSize: theme.fontSize.sm,
  },
  timelineContent: {
    marginBottom: theme.spacing.md,
  },
  dominant: {
    flexDirection: 'row',
    marginBottom: theme.spacing.sm,
  },
  dominantLabel: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.medium,
    color: theme.colors.text.secondary,
  },
  dominantValue: {
    color: theme.colors.emotional.calm,
    fontWeight: theme.fontWeight.semibold,
  },
  range: {
    fontSize: theme.fontSize.xs,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.sm,
  },
  timelineBar: {
    flexDirection: 'row',
    height: 32,
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
  },
  timelineSegment1: {
    flex: 1,
    backgroundColor: theme.colors.emotional.elevated,
  },
  timelineSegment2: {
    flex: 1,
    backgroundColor: theme.colors.emotional.neutral,
  },
  timelineSegment3: {
    flex: 1,
    backgroundColor: theme.colors.emotional.elevated,
  },
  timelineSegment4: {
    flex: 9,
    backgroundColor: theme.colors.emotional.calm,
  },
});
