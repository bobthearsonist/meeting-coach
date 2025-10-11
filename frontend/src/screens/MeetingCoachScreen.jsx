import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import theme from '../utils/theme';

/**
 * MeetingCoachScreen - Main screen for the Meeting Coach application
 *
 * This is the coarse-grained screen layout that will be progressively refined
 * into focused subcomponents:
 * - Header with status indicator
 * - Status dashboard with emotional state, social cues, confidence, speech pace
 * - Emotional timeline visualization
 * - Recent activity feed (transcripts)
 * - Session stats footer
 *
 * Future iterations will extract these into dedicated components and wire them
 * to Context/hooks for real-time WebSocket data.
 */
export default function MeetingCoachScreen() {
  const handleSettingsPress = () => {
    // TODO: Open settings modal/sheet
    console.log('Settings pressed');
  };

  const handleHistoryPress = () => {
    // TODO: Open history modal/sheet
    console.log('History pressed');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header Section */}
        <View style={styles.section}>
          <View style={styles.header}>
            <View style={styles.headerLeft}>
              <Text style={styles.emoji}>🧠</Text>
              <View>
                <Text style={styles.headerTitle}>
                  Live Emotional Monitoring
                </Text>
                <Text style={styles.headerSubtitle}>
                  Autism/ADHD Meeting Coach
                </Text>
              </View>
            </View>
            <View style={styles.headerRight}>
              <TouchableOpacity
                style={styles.iconButton}
                onPress={handleHistoryPress}
                testID="history-button"
              >
                <Text style={styles.iconButtonText}>📜</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.iconButton}
                onPress={handleSettingsPress}
                testID="settings-button"
              >
                <Text style={styles.iconButtonText}>⚙️</Text>
              </TouchableOpacity>
              <View style={styles.recording}>
                <View style={styles.recordingDot} />
                <Text style={styles.recordingText}>Recording</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Status Dashboard */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📊 Current Status</Text>

          <View style={styles.statusGrid}>
            <View style={[styles.statusBox, styles.emotionalState]}>
              <Text style={styles.statusLabel}>Emotional State</Text>
              <Text
                style={[
                  styles.statusValue,
                  { color: theme.colors.emotional.calm },
                ]}
              >
                calm
              </Text>
            </View>
            <View style={[styles.statusBox, styles.socialCues]}>
              <Text style={styles.statusLabel}>Social Cues</Text>
              <Text
                style={[
                  styles.statusValue,
                  { color: theme.colors.social.appropriate },
                ]}
              >
                appropriate
              </Text>
            </View>
            <View style={[styles.statusBox, styles.confidence]}>
              <Text style={styles.statusLabel}>Confidence</Text>
              <Text
                style={[styles.statusValue, { color: theme.colors.confidence }]}
              >
                0.9
              </Text>
            </View>
            <View style={[styles.statusBox, styles.speechPace]}>
              <Text style={styles.statusLabel}>Speech Pace</Text>
              <Text
                style={[
                  styles.statusValue,
                  { color: theme.colors.status.success },
                ]}
              >
                150<Text style={styles.unit}> WPM</Text>
              </Text>
            </View>
          </View>

          <View style={styles.alert}>
            <Text style={styles.checkMark}>✓</Text>
            <Text style={styles.alertText}>All good – no alerts</Text>
          </View>
        </View>

        {/* Emotional Timeline */}
        <View style={styles.section}>
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

        {/* Recent Activity Feed */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>💬 Recent Activity</Text>

          <View style={styles.activityList}>
            <View style={styles.activityItem}>
              <Text style={styles.timestamp}>17:21:57</Text>
              <View style={styles.activityDot} />
              <Text style={styles.activityText}>
                "All right, so I think it's only fair that the guys that helped
                us build this car see how well their work is holding up."
              </Text>
            </View>

            <View style={styles.activityItem}>
              <Text style={styles.timestamp}>17:21:49</Text>
              <View style={styles.activityDot} />
              <Text style={styles.activityText}>
                "I'm not really sure. If I had the right list job from 1 to 10,
                I'm giving it a million because no one wants to do this. It's
                just not gonna happen."
              </Text>
            </View>

            <View style={styles.activityItem}>
              <Text style={styles.timestamp}>17:21:40</Text>
              <View style={styles.activityDot} />
              <Text style={styles.activityText}>
                "Really bad. This deal is probably making us not able to take
                this to a free jump and fix it because it's just too far
                down..."
              </Text>
            </View>
          </View>
        </View>

        {/* Session Stats Footer */}
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
              <Text style={{ color: theme.colors.emotional.calm }}>●</Text>{' '}
              calm: 43%
            </Text>
            <Text style={styles.emotion}>
              <Text style={{ color: theme.colors.emotional.neutral }}>●</Text>{' '}
              neutral: 36%
            </Text>
            <Text style={styles.emotion}>
              <Text style={{ color: theme.colors.emotional.elevated }}>●</Text>{' '}
              engaged: 21%
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  content: {
    flex: 1,
    padding: theme.spacing.lg,
  },
  section: {
    backgroundColor: theme.colors.background.primary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.light,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.md,
    flex: 1,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.md,
  },
  iconButton: {
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.lg,
    backgroundColor: theme.colors.background.secondary,
  },
  iconButtonText: {
    fontSize: theme.fontSize.xl,
  },
  emoji: {
    fontSize: theme.fontSize.huge,
  },
  headerTitle: {
    fontSize: theme.fontSize.xl,
    fontWeight: theme.fontWeight.bold,
    color: theme.colors.text.primary,
  },
  headerSubtitle: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.text.secondary,
  },
  recording: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.background.errorTint,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.xl,
    gap: theme.spacing.sm,
  },
  recordingDot: {
    width: 8,
    height: 8,
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.recording,
  },
  recordingText: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.medium,
    color: theme.colors.status.error,
  },
  sectionTitle: {
    fontSize: theme.fontSize.lg,
    fontWeight: theme.fontWeight.semibold,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.lg,
  },
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
  },
  statusBox: {
    flex: 1,
    minWidth: 100,
    padding: theme.spacing.lg,
    borderRadius: theme.borderRadius.md,
    borderLeftWidth: 4,
  },
  emotionalState: {
    backgroundColor: theme.colors.background.calmTint,
    borderLeftColor: theme.colors.emotional.calm,
  },
  socialCues: {
    backgroundColor: theme.colors.background.engagedTint,
    borderLeftColor: theme.colors.social.appropriate,
  },
  confidence: {
    backgroundColor: theme.colors.background.confidenceTint,
    borderLeftColor: theme.colors.confidence,
  },
  speechPace: {
    backgroundColor: theme.colors.background.successTint,
    borderLeftColor: theme.colors.status.success,
  },
  statusLabel: {
    fontSize: theme.fontSize.xs,
    fontWeight: theme.fontWeight.medium,
    color: theme.colors.text.secondary,
    marginBottom: 4,
  },
  statusValue: {
    fontSize: theme.fontSize.xxl,
    fontWeight: theme.fontWeight.bold,
  },
  unit: {
    fontSize: theme.fontSize.sm,
  },
  alert: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.background.successTint,
    borderWidth: 1,
    borderColor: theme.colors.borderTint.success,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    gap: theme.spacing.sm,
  },
  checkMark: {
    color: theme.colors.status.success,
    fontSize: theme.fontSize.xl,
  },
  alertText: {
    fontSize: theme.fontSize.sm,
    fontWeight: theme.fontWeight.medium,
    color: theme.colors.status.success,
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
  activityList: {
    gap: theme.spacing.md,
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
