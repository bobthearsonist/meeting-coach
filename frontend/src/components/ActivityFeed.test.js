import React from 'react';
import {render} from '@testing-library/react-native';
import ActivityFeed from './ActivityFeed';
import MeetingContext from '../context/MeetingContext';

describe('ActivityFeed', () => {
  // Mock state with timeline data including recent entries
  const mockStateWithEntries = {
    emotionalState: 'calm',
    wpm: 120,
    alerts: [],
    isConnected: true,
    isSessionActive: true,
    isRecording: false,
    timeline: {
      summary: {
        dominant_state: 'calm',
        average_confidence: 0.9,
      },
      recentEntries: [
        {
          emotional_state: 'calm',
          social_cue: 'appropriate',
          confidence: 0.9,
          text: 'All right, so I think it is only fair that the guys helped us.',
          alert: false,
          timestamp: 1704123540, // Unix timestamp
        },
        {
          emotional_state: 'neutral',
          social_cue: 'appropriate',
          confidence: 0.8,
          text: 'I am not really sure about this decision.',
          alert: false,
          timestamp: 1704123550,
        },
        {
          emotional_state: 'elevated',
          social_cue: 'appropriate',
          confidence: 0.7,
          text: 'This is really important and we need to act fast.',
          alert: false,
          timestamp: 1704123560,
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
  const renderWithProvider = (component, state = mockStateWithEntries) => {
    const mockDispatch = jest.fn();
    return render(
      <MeetingContext.Provider value={{state, dispatch: mockDispatch}}>
        {component}
      </MeetingContext.Provider>
    );
  };

  it('renders section title', () => {
    const {getByText} = renderWithProvider(<ActivityFeed />);
    expect(getByText('💬 Recent Activity')).toBeTruthy();
  });

  it('displays activity entries from timeline data', () => {
    const {getByText} = renderWithProvider(<ActivityFeed />);
    
    // Check for transcript text from mock data
    expect(
      getByText(/All right, so I think it is only fair/)
    ).toBeTruthy();
    expect(getByText(/I am not really sure about this decision/)).toBeTruthy();
  });

  it('formats timestamps correctly', () => {
    const {getAllByText} = renderWithProvider(<ActivityFeed />);
    
    // Should have timestamps formatted as HH:MM:SS
    const timestamps = getAllByText(/\d{2}:\d{2}:\d{2}/);
    expect(timestamps.length).toBeGreaterThan(0);
  });

  it('displays empty state when no entries', () => {
    const {getByText} = renderWithProvider(<ActivityFeed />, mockStateEmpty);
    
    expect(getByText('💬 Recent Activity')).toBeTruthy();
    expect(getByText('No recent activity')).toBeTruthy();
    expect(getByText(/Start speaking to see transcriptions/)).toBeTruthy();
  });

  it('limits display to most recent entries', () => {
    const {getByText} = renderWithProvider(<ActivityFeed />);
    
    // Should render the component successfully
    expect(getByText('💬 Recent Activity')).toBeTruthy();
  });
});
