import React, { useMemo } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import useMeetingData from '../hooks/useMeetingData';
import theme, { commonStyles } from '../utils/theme';

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
 * Wire to real timeline data from backend via timeline_update WebSocket messages.
 *
 * SLIDING WINDOW: Filters entries to show only the last 5 minutes of data,
 * creating a proper sliding time window that moves forward as new data arrives.
 *
 * Accesses global state via useMeetingData hook.
 */
export default function EmotionalTimeline() {
  const { timeline } = useMeetingData();

  // Emoji mapping for emotional states
  const emojiMap = {
    calm: '🧘',
    neutral: '😐',
    engaged: '✨',
    elevated: '⬆️',
    intense: '🔥',
    rapid: '⚡',
    overwhelmed: '😵‍💫',
    distracted: '🤔',
    unknown: '❓',
  };

  // Filter entries to last 5 minutes (sliding window)
  const windowedEntries = useMemo(() => {
    if (!timeline?.recentEntries || timeline.recentEntries.length === 0) {
      return [];
    }

    const entries = timeline.recentEntries;
    const latestTimestamp = entries[entries.length - 1].timestamp;
    const fiveMinutesAgo = latestTimestamp - 5 * 60; // 5 minutes in seconds

    // Filter to only entries within the last 5 minutes
    return entries.filter((entry) => entry.timestamp >= fiveMinutesAgo);
  }, [timeline?.recentEntries]);

  // Calculate time range from windowed entries
  const timeRange = useMemo(() => {
    if (windowedEntries.length === 0) {
      return 'No data';
    }

    const oldestTimestamp = windowedEntries[0].timestamp;
    const newestTimestamp =
      windowedEntries[windowedEntries.length - 1].timestamp;

    const formatTime = (timestamp) => {
      const date = new Date(timestamp * 1000); // Convert from Unix timestamp
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      });
    };

    return `${formatTime(oldestTimestamp)} – ${formatTime(newestTimestamp)}`;
  }, [windowedEntries]);

  // Calculate dominant state and average confidence from windowed entries
  const { dominantState, averageConfidence, stateDistribution } =
    useMemo(() => {
      if (windowedEntries.length === 0) {
        return {
          dominantState: 'unknown',
          averageConfidence: 0.0,
          stateDistribution: {},
        };
      }

      // Build state distribution from windowed entries
      const distribution = {};
      let totalConfidence = 0;

      windowedEntries.forEach((entry) => {
        const state = entry.emotional_state || 'neutral';
        distribution[state] = (distribution[state] || 0) + 1;
        totalConfidence += entry.confidence || 0;
      });

      // Find dominant state
      const dominant = Object.entries(distribution).reduce(
        (max, [state, count]) => (count > max.count ? { state, count } : max),
        { state: 'unknown', count: 0 }
      );

      return {
        dominantState: dominant.state,
        averageConfidence: totalConfidence / windowedEntries.length,
        stateDistribution: distribution,
      };
    }, [windowedEntries]);

  // Calculate timeline segments based on state distribution from windowed entries
  const timelineSegments = useMemo(() => {
    if (!stateDistribution || Object.keys(stateDistribution).length === 0) {
      return [
        { state: 'unknown', flex: 1, color: theme.colors.emotional.neutral },
      ];
    }

    return Object.entries(stateDistribution).map(([state, count]) => ({
      state,
      flex: count,
      color: theme.colors.emotional[state] || theme.colors.emotional.neutral,
    }));
  }, [stateDistribution]);

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
            <Text style={styles.dominantValue}>
              {emojiMap[dominantState] || '❓'} {dominantState.toUpperCase()} (
              {averageConfidence.toFixed(1)})
            </Text>
          </Text>
        </View>
        <Text style={styles.range}>Range: {timeRange}</Text>

        <View style={styles.timelineBar}>
          {timelineSegments.map((segment, index) => (
            <View
              key={`${segment.state}-${index}`}
              style={[
                styles.timelineSegment,
                { flex: segment.flex, backgroundColor: segment.color },
              ]}
            />
          ))}
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
  timelineSegment: {
    // Dynamic flex and backgroundColor set inline based on data
  },
});
