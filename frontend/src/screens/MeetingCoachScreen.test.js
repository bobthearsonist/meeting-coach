import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import MeetingCoachScreen from './MeetingCoachScreen';

describe('MeetingCoachScreen', () => {
  it('renders without crashing', () => {
    const { getByText } = render(<MeetingCoachScreen />);

    // Verify main sections are rendered
    expect(getByText('Live Emotional Monitoring')).toBeTruthy();
    expect(getByText('Autism/ADHD Meeting Coach')).toBeTruthy();
  });

  it('displays status dashboard', () => {
    const { getByText } = render(<MeetingCoachScreen />);

    expect(getByText('📊 Current Status')).toBeTruthy();
    expect(getByText('Emotional State')).toBeTruthy();
    expect(getByText('Social Cues')).toBeTruthy();
    expect(getByText('Confidence')).toBeTruthy();
    expect(getByText('Speech Pace')).toBeTruthy();
  });

  it('displays emotional timeline', () => {
    const { getByText } = render(<MeetingCoachScreen />);

    expect(getByText('📈 Emotional Timeline')).toBeTruthy();
    expect(getByText('Last 5 minutes')).toBeTruthy();
  });

  it('displays recent activity feed', () => {
    const { getByText } = render(<MeetingCoachScreen />);

    expect(getByText('💬 Recent Activity')).toBeTruthy();
  });

  it('displays session stats footer', () => {
    const { getByText } = render(<MeetingCoachScreen />);

    expect(getByText(/Duration:/)).toBeTruthy();
    expect(getByText(/Analyses:/)).toBeTruthy();
    expect(getByText(/Alerts:/)).toBeTruthy();
  });

  it('displays recording indicator', () => {
    const { getByText } = render(<MeetingCoachScreen />);

    expect(getByText('Recording')).toBeTruthy();
  });

  it('displays success alert when no issues', () => {
    const { getByText } = render(<MeetingCoachScreen />);

    expect(getByText('All good – no alerts')).toBeTruthy();
  });

  // Button interaction tests
  describe('Button Interactions', () => {
    it('should not throw when settings button is pressed', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const { getByTestId } = render(<MeetingCoachScreen />);

      const settingsButton = getByTestId('settings-button');
      expect(() => fireEvent.press(settingsButton)).not.toThrow();
      expect(consoleSpy).toHaveBeenCalledWith('Settings pressed');

      consoleSpy.mockRestore();
    });

    it('should not throw when history button is pressed', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const { getByTestId } = render(<MeetingCoachScreen />);

      const historyButton = getByTestId('history-button');
      expect(() => fireEvent.press(historyButton)).not.toThrow();
      expect(consoleSpy).toHaveBeenCalledWith('History pressed');

      consoleSpy.mockRestore();
    });
  });
});
