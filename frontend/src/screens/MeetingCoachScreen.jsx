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
import TopSessionDrawer from '../components/TopSessionDrawer';

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
    // Connect to WebSocket server with better error handling
    websocketService.connect().catch((err) => {
      console.warn(
        '⚠️ WebSocket connection failed - will auto-retry:',
        err.message
      );
      console.warn(
        '💡 Make sure backend is running: cd backend && python main.py'
      );
    });

    // Subscribe to connection status changes
    const unsubscribeStatus = websocketService.onStatusChange(({ status }) => {
      setConnectionStatus(status === ConnectionStatus.OPEN);

      // Log connection status for debugging
      if (status === ConnectionStatus.OPEN) {
        console.log('✅ WebSocket connected successfully');
      } else if (status === ConnectionStatus.RECONNECTING) {
        console.log('🔄 WebSocket reconnecting...');
      } else if (status === ConnectionStatus.CLOSED) {
        console.warn('❌ WebSocket disconnected');
      }
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
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
      >
        <View style={styles.content}>
          <TopSessionDrawer
            onHistoryPress={handleHistoryPress}
            onSettingsPress={handleSettingsPress}
          />
          {/* Status Dashboard */}
          <StatusPanel />

          {/* Emotional Timeline Visualization */}
          <EmotionalTimeline />

          {/* Recent Activity Feed */}
          <ActivityFeed />
        </View>
      </ScrollView>

      {/* Removed duplicate TopSessionDrawer */}

      {/* Session Stats Footer - Floating */}
      <SessionStats />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 140, // space for footer
  },
  content: {
    flex: 1,
    padding: theme.spacing.lg,
  },
  sectionTitle: {
    fontSize: theme.fontSize.lg,
    fontWeight: theme.fontWeight.semibold,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.lg,
  },
});
