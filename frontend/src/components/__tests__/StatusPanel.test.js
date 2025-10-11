import React from 'react';
import {render} from '@testing-library/react-native';
import StatusPanel from '../StatusPanel';
import {MeetingProvider} from '../../context/MeetingContext';

describe('StatusPanel', () => {
  const wrapper = ({children}) => <MeetingProvider>{children}</MeetingProvider>;

  it('renders section title', () => {
    const {getByText} = render(<StatusPanel />, {wrapper});
    expect(getByText('📊 Current Status')).toBeTruthy();
  });

  it('displays emotional state from context', () => {
    const {getByText} = render(<StatusPanel />, {wrapper});
    // Default state from MeetingContext is 'neutral'
    expect(getByText('neutral')).toBeTruthy();
  });

  it('displays WPM from context', () => {
    const {getByText} = render(<StatusPanel />, {wrapper});
    // Default WPM from MeetingContext is 0
    expect(getByText(/WPM/)).toBeTruthy();
  });

  it('displays all status labels', () => {
    const {getByText} = render(<StatusPanel />, {wrapper});
    expect(getByText('Emotional State')).toBeTruthy();
    expect(getByText('Social Cues')).toBeTruthy();
    expect(getByText('Confidence')).toBeTruthy();
    expect(getByText('Speech Pace')).toBeTruthy();
  });

  it('displays success alert', () => {
    const {getByText} = render(<StatusPanel />, {wrapper});
    expect(getByText('✓')).toBeTruthy();
    expect(getByText('All good – no alerts')).toBeTruthy();
  });
});
