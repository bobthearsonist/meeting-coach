import React, {useMemo} from 'react';
import {View, Text, StyleSheet} from 'react-native';
import useMeetingData from '../hooks/useMeetingData';
import theme, {commonStyles} from '../utils/theme';

/**
 * ActivityFeed - Displays recent transcription activity
 *
 * Shows:
 * - Recent Activity header
 * - List of recent transcript entries with timestamps and text
 * - Emotional state indicator dot for each entry
 *
 * LEARNING: This component displays a feed of recent transcription items
 * from the backend timeline data. Each item shows timestamp, emotional
 * indicator, and transcript text from real WebSocket updates.
 *
 * Wired to timeline.recentEntries from global state.
 */
export default function ActivityFeed() {
  const {timeline} = useMeetingData();

  // Format timestamp from Unix timestamp to HH:MM:SS
  const formatTimestamp = useMemo(
    () => timestamp => {
      const date = new Date(timestamp * 1000);
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      });
    },
    [],
  );

  // Get recent entries from timeline, limit to last 10
  const recentActivities = useMemo(() => {
    if (!timeline?.recentEntries || timeline.recentEntries.length === 0) {
      return [];
    }

    // Reverse to show newest first, take last 10
    return timeline.recentEntries
      .slice(-10)
      .reverse()
      .map((entry, index) => ({
        id: `${entry.timestamp}-${index}`,
        timestamp: formatTimestamp(entry.timestamp),
        text: entry.text || 'No text available',
        emotionalState: entry.emotional_state || 'neutral',
      }));
  }, [timeline?.recentEntries, formatTimestamp]);

  // Show message if no data
  if (recentActivities.length === 0) {
    return (
      <View style={styles.container}>
        <Text style={styles.sectionTitle}>💬 Recent Activity</Text>
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>No recent activity</Text>
          <Text style={styles.emptySubtext}>
            Start speaking to see transcriptions appear here
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>💬 Recent Activity</Text>

      <View style={styles.activityList}>
        {recentActivities.map(activity => (
          <View key={activity.id} style={styles.activityItem}>
            <Text style={styles.timestamp}>{activity.timestamp}</Text>
            <View
              style={[
                styles.activityDot,
                {
                  backgroundColor:
                    theme.colors.emotional[activity.emotionalState] ||
                    theme.colors.emotional.neutral,
                },
              ]}
            />
            <Text style={styles.activityText}>{activity.text}</Text>
          </View>
        ))}
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
    fontWeight: theme.fontWeight.semibold,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.lg,
  },
  activityList: {
    gap: theme.spacing.md,
  },
  emptyState: {
    padding: theme.spacing.xl,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyText: {
    fontSize: theme.fontSize.md,
    fontWeight: theme.fontWeight.medium,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.sm,
  },
  emptySubtext: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border.light,
    gap: theme.spacing.md,
  },
  timestamp: {
    width: 64,
    fontSize: theme.fontSize.xs,
    color: theme.colors.text.secondary,
  },
  activityDot: {
    width: 8,
    height: 8,
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.emotional.calm,
    marginTop: 4,
  },
  activityText: {
    flex: 1,
    fontSize: theme.fontSize.sm,
    color: theme.colors.text.primary,
    lineHeight: 18,
  },
});
