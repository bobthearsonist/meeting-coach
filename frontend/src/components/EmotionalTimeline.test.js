import React from 'react';
import {render} from '@testing-library/react-native';
import EmotionalTimeline from './EmotionalTimeline';
import MeetingContext from '../context/MeetingContext';

describe('EmotionalTimeline', () => {
  // Mock state with timeline data
  const mockStateWithTimeline = {
    emotionalState: 'calm',
    wpm: 120,
    alerts: [],
    isConnected: true,
    isSessionActive: true,
    isRecording: false,
    timeline: {
      summary: {
        session_duration_minutes: 5.2,
        total_entries: 12,
        dominant_state: 'calm',
        state_distribution: {
          calm: 9,
          neutral: 2,
          elevated: 1,
        },
        alert_count: 0,
        average_confidence: 0.9,
      },
      recentEntries: [
        {
          emotional_state: 'elevated',
          social_cue: 'appropriate',
          confidence: 0.8,
          text: 'Test entry 1',
          alert: false,
          timestamp: 1704123540, // 17:19:00
        },
        {
          emotional_state: 'calm',
          social_cue: 'appropriate',
          confidence: 0.9,
          text: 'Test entry 2',
          alert: false,
          timestamp: 1704123660, // 17:21:00
        },
      ],
    },
  };

  const mockStateEmpty = {
    emotionalState: 'neutral',
    wpm: 0,
    alerts: [],
    isConnected: false,
    isSessionActive: false,
    isRecording: false,
    timeline: {
      summary: null,
      recentEntries: [],
    },
  };

  // Wrapper component to provide MeetingContext with mock data
  const renderWithProvider = (component, state = mockStateWithTimeline) => {
    const mockDispatch = jest.fn();
    return render(
      <MeetingContext.Provider value={{state, dispatch: mockDispatch}}>
        {component}
      </MeetingContext.Provider>,
    );
  };

  it('renders section title', () => {
    const {getByText} = renderWithProvider(<EmotionalTimeline />);
    expect(getByText('📈 Emotional Timeline')).toBeTruthy();
  });

  it('displays time range indicator', () => {
    const {getByText} = renderWithProvider(<EmotionalTimeline />);
    expect(getByText('Last 5 minutes')).toBeTruthy();
  });

  it('displays dominant emotional state from timeline data', () => {
    const {getByText} = renderWithProvider(<EmotionalTimeline />);
    expect(getByText(/Dominant:/)).toBeTruthy();
    expect(getByText(/CALM/)).toBeTruthy();
    expect(getByText(/0\.9/)).toBeTruthy();
  });

  it('displays calculated time range from entries', () => {
    const {getByText} = renderWithProvider(<EmotionalTimeline />);
    expect(getByText(/Range:/)).toBeTruthy();
    // Time range is calculated from timestamps - just check that it's there
    expect(getByText(/Range:.*–/)).toBeTruthy();
  });

  it('handles empty timeline data gracefully', () => {
    const {getByText} = renderWithProvider(
      <EmotionalTimeline />,
      mockStateEmpty,
    );
    expect(getByText('📈 Emotional Timeline')).toBeTruthy();
    expect(getByText(/UNKNOWN/)).toBeTruthy();
    expect(getByText(/Range:.*No data/)).toBeTruthy();
  });
});
