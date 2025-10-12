import React from 'react';
import {View, Text, StyleSheet} from 'react-native';
import theme from '../utils/theme';

/**
 * SessionStats Component
 * 
 * Displays session statistics footer including:
 * - Duration: Total session time
 * - Analyses: Number of transcription analyses
 * - Alerts: Number of alerts triggered
 * - Emotion Distribution: Breakdown of emotional states as percentages
 */
const SessionStats = () => {
  return (
    <View style={styles.footer}>
      <View style={styles.stats}>
        <Text style={styles.stat}>
          Duration: <Text style={styles.statValue}>3.1 min</Text>
        </Text>
        <Text style={styles.stat}>
          Analyses: <Text style={styles.statValue}>14</Text>
        </Text>
        <Text style={styles.stat}>
          Alerts: <Text style={styles.statValue}>0</Text>
        </Text>
      </View>
      <View style={styles.emotionStats}>
        <Text style={styles.emotion}>
          <Text style={{color: theme.colors.emotional.calm}}>●</Text> calm: 43%
        </Text>
        <Text style={styles.emotion}>
          <Text style={{color: theme.colors.emotional.neutral}}>●</Text>{' '}
          neutral: 36%
        </Text>
        <Text style={styles.emotion}>
          <Text style={{color: theme.colors.emotional.elevated}}>●</Text>{' '}
          engaged: 21%
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  footer: {
    marginTop: theme.spacing.lg,
    backgroundColor: theme.colors.text.primary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
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
