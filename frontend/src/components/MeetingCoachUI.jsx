import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';

export default function MeetingCoachUI() {
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
              <View style={styles.recording}>
                <View style={styles.recordingDot} />
                <Text style={styles.recordingText}>Recording</Text>
              </View>
            </View>
          </View>

          {/* Status Dashboard */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>📊 Current Status</Text>

            <View style={styles.statusGrid}>
              <View style={[styles.statusBox, styles.emotionalState]}>
                <Text style={styles.statusLabel}>Emotional State</Text>
                <Text style={[styles.statusValue, { color: '#16a34a' }]}>
                  calm
                </Text>
              </View>
              <View style={[styles.statusBox, styles.socialCues]}>
                <Text style={styles.statusLabel}>Social Cues</Text>
                <Text style={[styles.statusValue, { color: '#2563eb' }]}>
                  appropriate
                </Text>
              </View>
              <View style={[styles.statusBox, styles.confidence]}>
                <Text style={styles.statusLabel}>Confidence</Text>
                <Text style={[styles.statusValue, { color: '#9333ea' }]}>
                  0.9
                </Text>
              </View>
              <View style={[styles.statusBox, styles.speechPace]}>
                <Text style={styles.statusLabel}>Speech Pace</Text>
                <Text style={[styles.statusValue, { color: '#16a34a' }]}>
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
                  "All right, so I think it's only fair that the guys that
                  helped us build this car see how well their work is holding
                  up."
                </Text>
              </View>

              <View style={styles.activityItem}>
                <Text style={styles.timestamp}>17:21:49</Text>
                <View style={styles.activityDot} />
                <Text style={styles.activityText}>
                  "I'm not really sure. If I had the right list job from 1 to
                  10, I'm giving it a million because no one wants to do this.
                  It's just not gonna happen."
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
                <Text style={{ color: '#4ade80' }}>●</Text> calm: 43%
              </Text>
              <Text style={styles.emotion}>
                <Text style={{ color: '#9ca3af' }}>●</Text> neutral: 36%
              </Text>
              <Text style={styles.emotion}>
                <Text style={{ color: '#fbbf24' }}>●</Text> engaged: 21%
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
    backgroundColor: '#ffffff',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  section: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  emoji: {
    fontSize: 36,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  headerSubtitle: {
    fontSize: 12,
    color: '#6b7280',
  },
  recording: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fef2f2',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    gap: 8,
  },
  recordingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ef4444',
  },
  recordingText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#dc2626',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 16,
  },
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
    marginBottom: 16,
  },
  statusBox: {
    flex: 1,
    minWidth: 100,
    padding: 16,
    borderRadius: 8,
    borderLeftWidth: 4,
  },
  emotionalState: {
    backgroundColor: '#f0fdf4',
    borderLeftColor: '#22c55e',
  },
  socialCues: {
    backgroundColor: '#eff6ff',
    borderLeftColor: '#3b82f6',
  },
  confidence: {
    backgroundColor: '#faf5ff',
    borderLeftColor: '#a855f7',
  },
  speechPace: {
    backgroundColor: '#f0fdf4',
    borderLeftColor: '#22c55e',
  },
  statusLabel: {
    fontSize: 10,
    fontWeight: '500',
    color: '#6b7280',
    marginBottom: 4,
  },
  statusValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  unit: {
    fontSize: 12,
  },
  alert: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0fdf4',
    borderWidth: 1,
    borderColor: '#dcfce7',
    borderRadius: 8,
    padding: 12,
    gap: 8,
  },
  checkMark: {
    color: '#22c55e',
    fontSize: 18,
  },
  alertText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#15803d',
  },
  timelineHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  timeText: {
    color: '#6b7280',
    fontSize: 12,
  },
  timelineContent: {
    marginBottom: 12,
  },
  dominant: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  dominantLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#6b7280',
  },
  dominantValue: {
    color: '#16a34a',
    fontWeight: '600',
  },
  range: {
    fontSize: 10,
    color: '#6b7280',
    marginBottom: 8,
  },
  timelineBar: {
    flexDirection: 'row',
    height: 32,
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
    overflow: 'hidden',
  },
  timelineSegment1: {
    flex: 1,
    backgroundColor: '#fbbf24',
  },
  timelineSegment2: {
    flex: 1,
    backgroundColor: '#d1d5db',
  },
  timelineSegment3: {
    flex: 1,
    backgroundColor: '#fbbf24',
  },
  timelineSegment4: {
    flex: 9,
    backgroundColor: '#22c55e',
  },
  activityList: {
    gap: 12,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 12,
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    gap: 12,
  },
  timestamp: {
    width: 64,
    fontSize: 10,
    color: '#6b7280',
  },
  activityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#22c55e',
    marginTop: 4,
  },
  activityText: {
    flex: 1,
    fontSize: 12,
    color: '#374151',
    lineHeight: 18,
  },
  footer: {
    marginTop: 16,
    backgroundColor: '#1f2937',
    borderRadius: 8,
    padding: 16,
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
    gap: 24,
  },
  stat: {
    fontSize: 12,
    color: '#d1d5db',
  },
  statValue: {
    fontWeight: '600',
    color: '#ffffff',
  },
  emotionStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 16,
  },
  emotion: {
    fontSize: 10,
    color: '#d1d5db',
  },
});
