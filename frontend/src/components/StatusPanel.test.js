import React from 'react';
import {render} from '@testing-library/react-native';
import StatusPanel from './StatusPanel';
import {MeetingContext} from '../context/MeetingContext';

describe('StatusPanel', () => {
  const mockStateWithTimeline = {
    emotionalState: 'calm',
    wpm: 120,
    timeline: {
      summary: {
        average_confidence: 0.85,
        alert_count: 0,
      },
      recentEntries: [
        {
          timestamp: 1704123540,
          emotional_state: 'calm',
          social_cue: 'appropriate',
          confidence: 0.85,
          text: 'Sample text',
        },
      ],
    },
  };

  const mockStateWithAlerts = {
    emotionalState: 'elevated',
    wpm: 150,
    timeline: {
      summary: {
        average_confidence: 0.72,
        alert_count: 2,
      },
      recentEntries: [
        {
          timestamp: 1704123550,
          emotional_state: 'elevated',
          social_cue: 'interrupting',
          confidence: 0.72,
          text: 'Sample text',
        },
      ],
    },
  };

  const mockStateEmpty = {
    emotionalState: 'neutral',
    wpm: 0,
    timeline: {
      summary: null,
      recentEntries: [],
    },
  };

  const renderWithProvider = (mockState = mockStateWithTimeline) => {
    return render(
      <MeetingContext.Provider value={{state: mockState, dispatch: jest.fn()}}>
        <StatusPanel />
      </MeetingContext.Provider>,
    );
  };

  it('renders section title', () => {
    const {getByText} = renderWithProvider();
    expect(getByText('📊 Current Status')).toBeTruthy();
  });

  it('displays emotional state from context', () => {
    const {getByText} = renderWithProvider();
    expect(getByText('calm')).toBeTruthy();
  });

  it('displays WPM from context', () => {
    const {getByText} = renderWithProvider();
    expect(getByText(/120/)).toBeTruthy();
    expect(getByText(/WPM/)).toBeTruthy();
  });

  it('displays all status labels', () => {
    const {getByText} = renderWithProvider();
    expect(getByText('Emotional State')).toBeTruthy();
    expect(getByText('Social Cues')).toBeTruthy();
    expect(getByText('Confidence')).toBeTruthy();
    expect(getByText('Speech Pace')).toBeTruthy();
  });

  it('displays social cue from timeline', () => {
    const {getByText} = renderWithProvider();
    expect(getByText('appropriate')).toBeTruthy();
  });

  it('displays confidence from timeline summary', () => {
    const {getByText} = renderWithProvider();
    expect(getByText('0.85')).toBeTruthy();
  });

  it('displays success message when no alerts', () => {
    const {getByText} = renderWithProvider();
    expect(getByText('✓')).toBeTruthy();
    expect(getByText('All good – no alerts')).toBeTruthy();
  });

  it('displays alert count when alerts exist', () => {
    const {getByText} = renderWithProvider(mockStateWithAlerts);
    expect(getByText('⚠️')).toBeTruthy();
    expect(getByText('2 alerts')).toBeTruthy();
  });

  it('displays concerning social cue', () => {
    const {getByText} = renderWithProvider(mockStateWithAlerts);
    expect(getByText('interrupting')).toBeTruthy();
  });

  it('handles empty timeline gracefully', () => {
    const {getByText} = renderWithProvider(mockStateEmpty);
    expect(getByText('appropriate')).toBeTruthy(); // Default value
    expect(getByText('0.00')).toBeTruthy(); // Default confidence
    expect(getByText('All good – no alerts')).toBeTruthy();
  });
});
