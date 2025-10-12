import React, { useMemo } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import theme from '../utils/theme';
import useMeetingData from '../hooks/useMeetingData';

/**
 * SessionStats Component
 *
 * Displays session statistics footer including:
 * - Duration: Total session time
 * - Analyses: Number of transcription analyses
 * - Alerts: Number of alerts triggered
 * - Emotion Distribution: Breakdown of emotional states as percentages
 *
 * Wired to timeline data from global state via useMeetingData hook.
 */
const SessionStats = () => {
  const { timeline } = useMeetingData();

  // Calculate session duration from first to last entry
  const duration = useMemo(() => {
    const allEntries = timeline?.allEntries || timeline?.recentEntries;
    if (!allEntries || allEntries.length < 2) {
      return '0.0 min';
    }

    const firstTimestamp = allEntries[0].timestamp;
    const lastTimestamp = allEntries[allEntries.length - 1].timestamp;
    const durationSeconds = lastTimestamp - firstTimestamp;
    const minutes = (durationSeconds / 60).toFixed(1);

    return `${minutes} min`;
  }, [timeline?.allEntries, timeline?.recentEntries]);

  // Get analyses count (number of entries)
  const analysesCount = timeline?.recentEntries?.length || 0;

  // Get alert count from summary
  const alertCount = timeline?.summary?.alert_count || 0;

  // Calculate emotion distribution percentages
  const emotionDistribution = useMemo(() => {
    const stateDistribution = timeline?.summary?.state_distribution || {};
    const totalCount = Object.values(stateDistribution).reduce(
      (sum, count) => sum + count,
      0
    );

    if (totalCount === 0) {
      return [];
    }

    return Object.entries(stateDistribution)
      .map(([state, count]) => ({
        state,
        percentage: ((count / totalCount) * 100).toFixed(0),
        color: theme.colors.emotional[state] || theme.colors.emotional.neutral,
      }))
      .sort((a, b) => b.percentage - a.percentage) // Sort by percentage descending
      .slice(0, 3); // Show top 3
  }, [timeline?.summary?.state_distribution]);

  return (
    <View style={styles.footer}>
      <View style={styles.stats}>
        <Text style={styles.stat}>
          Duration: <Text style={styles.statValue}>{duration}</Text>
        </Text>
        <Text style={styles.stat}>
          Analyses: <Text style={styles.statValue}>{analysesCount}</Text>
        </Text>
        <Text style={styles.stat}>
          Alerts: <Text style={styles.statValue}>{alertCount}</Text>
        </Text>
      </View>
      <View style={styles.emotionStats}>
        {emotionDistribution.length > 0 ? (
          emotionDistribution.map((emotion, index) => (
            <Text key={emotion.state} style={styles.emotion}>
              <Text style={{ color: emotion.color }}>●</Text> {emotion.state}:{' '}
              {emotion.percentage}%
            </Text>
          ))
        ) : (
          <Text style={styles.emotion}>No emotion data yet</Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: theme.colors.text.primary,
    borderTopLeftRadius: theme.borderRadius.md,
    borderTopRightRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5, // Android shadow
    zIndex: 1000,
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.md,
    gap: theme.spacing.xxl,
  },
  stat: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.border.medium,
  },
  statValue: {
    fontWeight: theme.fontWeight.semibold,
    color: theme.colors.text.inverse,
  },
  emotionStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: theme.spacing.lg,
  },
  emotion: {
    fontSize: theme.fontSize.xs,
    color: theme.colors.border.medium,
  },
});

export default SessionStats;
