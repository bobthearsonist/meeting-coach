/**
 * Theme Configuration
 *
 * LEARNING: Centralizing design tokens (colors, spacing, typography) makes your app
 * consistent and easy to update. Instead of hardcoding '#1f2937' everywhere,
 * we use theme.colors.text.primary.
 */

export const theme = {
  // Color palette - matches the Python backend's color system
  colors: {
    // Emotional states (from backend/colors.py)
    emotional: {
      calm: '#4ade80', // Green - relaxed, comfortable
      engaged: '#fbbf24', // Amber - focused, interested (bright yellow in terminal)
      elevated: '#fbbf24', // Amber - energized, excited
      intense: '#fb923c', // Orange - strong emotion
      rapid: '#d946ef', // Magenta - fast-paced, quick speech
      overwhelmed: '#ef4444', // Red - stressed, overstimulated
      distracted: '#6b7280', // Gray - unfocused, wandering attention
      overly_critical: '#dc2626', // Dark red - harsh, judgmental tone
      neutral: '#9ca3af', // Gray - baseline state
      unknown: '#6b7280', // Dark gray - no data
    },

    // Social cues
    social: {
      appropriate: '#2563eb', // Blue - good social awareness
      'watch carefully': '#fbbf24', // Amber - be mindful
      concerning: '#ef4444', // Red - social misstep
      unknown: '#6b7280', // Gray - no data
    },

    // UI colors
    text: {
      primary: '#1f2937', // Dark gray - main text
      secondary: '#6b7280', // Medium gray - labels, less important
      tertiary: '#9ca3af', // Light gray - subtle text
      inverse: '#ffffff', // White - text on dark backgrounds
    },

    background: {
      primary: '#ffffff', // White - main background
      secondary: '#f9fafb', // Very light gray - cards, sections
      tertiary: '#f3f4f6', // Light gray - hover states
      // Tinted backgrounds for status cards
      calmTint: '#f0fdf4', // Very light green
      engagedTint: '#eff6ff', // Very light blue
      confidenceTint: '#faf5ff', // Very light purple
      successTint: '#f0fdf4', // Very light green (for success states)
      errorTint: '#fef2f2', // Very light red (for errors/alerts)
    },

    borderTint: {
      success: '#dcfce7', // Light green border
      error: '#fecaca', // Light red border
    },

    border: {
      light: '#e5e7eb', // Light border
      medium: '#d1d5db', // Medium border
      dark: '#9ca3af', // Dark border
    },

    status: {
      success: '#16a34a', // Green - all good
      warning: '#f59e0b', // Amber - warning
      error: '#dc2626', // Red - error/alert
      info: '#2563eb', // Blue - information
    },

    // Special
    recording: '#ef4444', // Red - recording indicator
    confidence: '#9333ea', // Purple - confidence score
  },

  // Spacing scale (in pixels, React Native uses numbers not strings)
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    xxl: 24,
    xxxl: 32,
  },

  // Typography
  fontSize: {
    xs: 10,
    sm: 12,
    base: 14,
    lg: 16,
    xl: 18,
    xxl: 20,
    xxxl: 24,
    huge: 36,
  },

  fontWeight: {
    normal: 'normal',
    medium: '500',
    semibold: '600',
    bold: 'bold',
  },

  // Border radius
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    full: 9999,
  },

  // Shadows (for iOS/macOS)
  shadow: {
    sm: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.05,
      shadowRadius: 2,
      elevation: 1,
    },
    md: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    lg: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 4,
    },
  },
};

/**
 * Helper function to get emotional state color
 * @param {string} state - Emotional state name
 * @returns {string} Hex color code
 */
export const getEmotionalColor = (state) => {
  const normalizedState = state?.toLowerCase() || 'unknown';
  return (
    theme.colors.emotional[normalizedState] || theme.colors.emotional.unknown
  );
};

/**
 * Helper function to get social cue color
 * @param {string} cue - Social cue name
 * @returns {string} Hex color code
 */
export const getSocialColor = (cue) => {
  const normalizedCue = cue?.toLowerCase() || 'unknown';
  return theme.colors.social[normalizedCue] || theme.colors.social.unknown;
};

/**
 * Common style patterns used across components
 *
 * LEARNING: Shared style objects reduce duplication and ensure consistency.
 * Later we can convert these to a wrapper component for dynamic theming (dark mode).
 */
export const commonStyles = {
  /**
   * Standard section container with border and padding
   * Used for StatusPanel, EmotionalTimeline, ActivityFeed, etc.
   */
  section: {
    backgroundColor: theme.colors.background.primary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.light,
  },
};

export default theme;
