import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated, Easing, PanResponder } from 'react-native';
import useMeetingData from '../hooks/useMeetingData';
import theme from '../utils/theme';

/**
 * TopSessionDrawer
 * Minimal collapsible top drawer showing only two navigation rows when expanded.
 * Collapsed: just a small drag handle bar.
 */
export default function TopSessionDrawer({ onHistoryPress, onSettingsPress }) {
  const { isRecording, isConnected } = useMeetingData();
  const [expanded, setExpanded] = useState(false); // start collapsed
  const animated = useRef(new Animated.Value(0)).current; // 0 collapsed, 1 expanded

  // Run animation when expanded toggles
  useEffect(() => {
    Animated.timing(animated, {
      toValue: expanded ? 1 : 0,
      duration: 260,
      easing: Easing.out(Easing.quad),
      useNativeDriver: false,
    }).start();
  }, [expanded, animated]);

  // Interpolated styles
  const containerHeight = animated.interpolate({
    inputRange: [0, 1],
    outputRange: [50, 170], // collapsed vs expanded heights (taller to fit status pill)
  });
  const detailOpacity = animated.interpolate({
    inputRange: [0, 0.4, 1],
    outputRange: [0, 0, 1],
  });

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dy) > 6,
      onPanResponderRelease: (_, gesture) => {
        if (gesture.dy < -25) {
          setExpanded(true);
        } else if (gesture.dy > 25) {
          setExpanded(false);
        } else {
          setExpanded(prev => !prev);
        }
      },
    })
  ).current;

  return (
    <Animated.View style={[styles.wrapper, { height: containerHeight }]} {...panResponder.panHandlers}>
      <TouchableOpacity
        activeOpacity={0.85}
        style={styles.handleContainer}
        onPress={() => setExpanded(!expanded)}
        accessibilityRole="button"
        accessibilityLabel={expanded ? 'Collapse drawer' : 'Expand drawer'}
      >
        <View style={styles.handle} />
        {!expanded && (
          <View style={[styles.statusPill, isRecording ? styles.statusRecording : (isConnected ? styles.statusConnected : styles.statusOffline)]}>
            <View style={[styles.statusDot, isRecording ? styles.dotRecording : (isConnected ? styles.dotConnected : styles.dotOffline)]} />
            <Text style={styles.statusText}>{isRecording ? 'Recording' : (isConnected ? 'Connected' : 'Offline')}</Text>
          </View>
        )}
      </TouchableOpacity>

      <Animated.View style={[styles.detailsContainer, { opacity: detailOpacity }]}>        
        {expanded && (
          <View style={styles.expandedStatusRow}>
            <View style={[styles.statusPill, isRecording ? styles.statusRecording : (isConnected ? styles.statusConnected : styles.statusOffline)]}>
              <View style={[styles.statusDot, isRecording ? styles.dotRecording : (isConnected ? styles.dotConnected : styles.dotOffline)]} />
              <Text style={styles.statusText}>{isRecording ? 'Recording' : (isConnected ? 'Connected' : 'Offline')}</Text>
            </View>
          </View>
        )}
        <View style={styles.list}>
          <TouchableOpacity
            style={styles.listItem}
            onPress={onHistoryPress}
            accessibilityRole="button"
            accessibilityLabel="View history"
          >
            <Text style={styles.listItemText}>📜  History</Text>
            <Text style={styles.listItemChevron}>›</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.listItem}
            onPress={onSettingsPress}
            accessibilityRole="button"
            accessibilityLabel="Open settings"
          >
            <Text style={styles.listItemText}>⚙️  Settings</Text>
            <Text style={styles.listItemChevron}>›</Text>
          </TouchableOpacity>
        </View>
      </Animated.View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    backgroundColor: theme.colors.background.secondary,
    paddingHorizontal: theme.spacing.lg,
    paddingTop: theme.spacing.sm,
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: theme.colors.border.light,
    marginBottom: theme.spacing.lg,
  },
  handleContainer: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
    gap: theme.spacing.sm,
    paddingBottom: theme.spacing.xs,
  },
  handle: {
    width: 54,
    height: 5,
    borderRadius: 3,
    backgroundColor: theme.colors.border.light,
    opacity: 0.9,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 14,
    gap: 6,
    backgroundColor: theme.colors.background.tertiary,
  },
  expandedStatusRow: {
    flexDirection: 'row',
    justifyContent: 'flex-start',
    marginBottom: theme.spacing.sm,
    paddingHorizontal: 2,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  dotRecording: { backgroundColor: theme.colors.status.error },
  dotConnected: { backgroundColor: theme.colors.status.success },
  dotOffline: { backgroundColor: theme.colors.text.secondary, opacity: 0.6 },
  statusRecording: { backgroundColor: theme.colors.background.tertiary },
  statusConnected: { backgroundColor: theme.colors.background.tertiary },
  statusOffline: { backgroundColor: theme.colors.background.tertiary },
  statusText: {
    fontSize: theme.fontSize.xs,
    fontWeight: theme.fontWeight.medium,
    color: theme.colors.text.primary,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  detailsContainer: {
    marginTop: theme.spacing.sm,
  },
  actionsRow: { },
  list: {
    marginTop: theme.spacing.xs,
    borderTopWidth: 1,
    borderColor: theme.colors.border.light,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: theme.spacing.sm + 2,
    borderBottomWidth: 1,
    borderColor: theme.colors.border.light,
  },
  listItemText: {
    fontSize: theme.fontSize.sm,
    color: theme.colors.text.primary,
    fontWeight: theme.fontWeight.medium,
    letterSpacing: 0.25,
  },
  listItemChevron: {
    fontSize: theme.fontSize.lg,
    color: theme.colors.text.secondary,
    opacity: 0.6,
    paddingHorizontal: theme.spacing.xs,
  },
  iconButton: {
    padding: theme.spacing.sm,
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.md,
  },
  iconText: { fontSize: theme.fontSize.lg },
});
