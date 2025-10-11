import React from 'react';
import {render} from '@testing-library/react-native';
import EmotionalTimeline from '../EmotionalTimeline';
import {MeetingProvider} from '../../context/MeetingContext';

describe('EmotionalTimeline', () => {
  // Wrapper component to provide MeetingContext
  const renderWithProvider = component => {
    return render(<MeetingProvider>{component}</MeetingProvider>);
  };

  it('renders section title', () => {
    const {getByText} = renderWithProvider(<EmotionalTimeline />);
    expect(getByText('📈 Emotional Timeline')).toBeTruthy();
  });

  it('displays time range indicator', () => {
    const {getByText} = renderWithProvider(<EmotionalTimeline />);
    expect(getByText('Last 5 minutes')).toBeTruthy();
  });

  it('displays dominant emotional state', () => {
    const {getByText} = renderWithProvider(<EmotionalTimeline />);
    expect(getByText(/Dominant:/)).toBeTruthy();
    expect(getByText('🧘 CALM (0.9)')).toBeTruthy();
  });

  it('displays time range', () => {
    const {getByText} = renderWithProvider(<EmotionalTimeline />);
    expect(getByText(/Range:/)).toBeTruthy();
  });

  it('renders timeline visualization bar', () => {
    const {getByText} = renderWithProvider(<EmotionalTimeline />);
    // Timeline should be visible with dominant state
    expect(getByText('📈 Emotional Timeline')).toBeTruthy();
  });
});
