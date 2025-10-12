import React, {useEffect} from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import theme, {commonStyles} from '../utils/theme';
import useMeetingData from '../hooks/useMeetingData';
import websocketService, {ConnectionStatus} from '../services/websocketService';
import StatusPanel from '../components/StatusPanel';
import EmotionalTimeline from '../components/EmotionalTimeline';
import ActivityFeed from '../components/ActivityFeed';
import SessionStats from '../components/SessionStats';

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
 * Now wired to Context/hooks for real-time WebSocket data.
 */
export default function MeetingCoachScreen() {
  // Access state and actions from our custom hook
  const {
    emotionalState,
    wpm,
    isConnected,
    isSessionActive,
    isRecording,
    updateEmotionalState,
    updateWpm,
    setConnectionStatus,
    setSessionStatus,
    setRecordingStatus,
    updateTimeline,
  } = useMeetingData();

  // Handle WebSocket connection and subscriptions (replaces componentDidMount/Unmount)
  useEffect(() => {
    // Connect to WebSocket server
    websocketService.connect('ws://localhost:8000').catch((err) => {
      console.error('Failed to connect to WebSocket:', err);
    });

    // Subscribe to connection status changes
    const unsubscribeStatus = websocketService.onStatusChange(({ status }) => {
      setConnectionStatus(status === ConnectionStatus.OPEN);
    });

    // Subscribe to meeting updates from backend
    const unsubscribeMeeting = websocketService.subscribe(
      'meeting_update',
      (payload) => {
        if (payload.emotional_state) {
          updateEmotionalState(payload.emotional_state);
        }
        if (payload.wpm !== undefined) {
          updateWpm(payload.wpm);
        }
      }
    );

    // Subscribe to session status (session started/stopped)
    const unsubscribeSession = websocketService.subscribe(
      'session_status',
      (payload) => {
        setSessionStatus(payload.status === 'started');
      }
    );

    // Subscribe to recording status (microphone listening state)
    const unsubscribeRecording = websocketService.subscribe(
      'recording_status',
      (payload) => {
        setRecordingStatus(payload.is_listening === true);
      }
    );

    // Subscribe to timeline updates from backend
    const unsubscribeTimeline = websocketService.subscribe(
      'timeline_update',
      (payload) => {
        updateTimeline(payload);
      }
    );

    // Cleanup on unmount (replaces componentWillUnmount)
    return () => {
      unsubscribeStatus();
      unsubscribeMeeting();
      unsubscribeSession();
      unsubscribeRecording();
      unsubscribeTimeline();
      websocketService.disconnect();
    };
  }, []); // Empty dependency array = run once on mount

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
                <View
                  style={[
                    styles.recordingDot,
                    isRecording && styles.recordingDotActive,
                  ]}
                />
                <Text style={styles.recordingText}>
                  {isRecording
                    ? 'Recording'
                    : isConnected
                    ? 'Connected'
                    : 'Disconnected'}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Status Dashboard */}
        <StatusPanel />

        {/* Emotional Timeline Visualization */}
        <EmotionalTimeline />

        {/* Recent Activity Feed */}
        <ActivityFeed />

        {/* Session Stats Footer */}
        <SessionStats />
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
    ...commonStyles.section,
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
});
