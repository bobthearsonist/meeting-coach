import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import MeetingCoachScreen from './MeetingCoachScreen';
import { MeetingProvider } from '../context/MeetingContext';

describe('MeetingCoachScreen', () => {
  // Wrapper component to provide MeetingContext
  const renderWithProvider = (component) => {
    return render(<MeetingProvider>{component}</MeetingProvider>);
  };

  it('renders without crashing', () => {
    const { getByText } = renderWithProvider(<MeetingCoachScreen />);

    // Verify main sections are rendered
    expect(getByText('Live Emotional Monitoring')).toBeTruthy();
    expect(getByText('Autism/ADHD Meeting Coach')).toBeTruthy();
  });

  it('displays status dashboard', () => {
    const { getByText } = renderWithProvider(<MeetingCoachScreen />);

    expect(getByText('📊 Current Status')).toBeTruthy();
    expect(getByText('Emotional State')).toBeTruthy();
    expect(getByText('Social Cues')).toBeTruthy();
    expect(getByText('Confidence')).toBeTruthy();
    expect(getByText('Speech Pace')).toBeTruthy();
  });

  it('displays emotional timeline', () => {
    const { getByText } = renderWithProvider(<MeetingCoachScreen />);

    expect(getByText('📈 Emotional Timeline')).toBeTruthy();
    expect(getByText('Last 5 minutes')).toBeTruthy();
  });

  it('displays recent activity feed', () => {
    const { getByText } = renderWithProvider(<MeetingCoachScreen />);

    expect(getByText('💬 Recent Activity')).toBeTruthy();
  });

  it('displays session stats footer', () => {
    const { getByText } = renderWithProvider(<MeetingCoachScreen />);

    expect(getByText(/Duration:/)).toBeTruthy();
    expect(getByText(/Analyses:/)).toBeTruthy();
    expect(getByText(/Alerts:/)).toBeTruthy();
  });

  it('displays recording indicator', () => {
    const { getByText } = renderWithProvider(<MeetingCoachScreen />);

    // Should display connection status (defaults to "Disconnected" in tests)
    expect(getByText('Disconnected')).toBeTruthy();
  });

  it('displays success alert when no issues', () => {
    const { getByText } = renderWithProvider(<MeetingCoachScreen />);

    expect(getByText('All good – no alerts')).toBeTruthy();
  });

  // Button interaction tests
  describe('Button Interactions', () => {
    it('should not throw when settings button is pressed', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const { getByTestId } = renderWithProvider(<MeetingCoachScreen />);

      const settingsButton = getByTestId('settings-button');
      expect(() => fireEvent.press(settingsButton)).not.toThrow();
      expect(consoleSpy).toHaveBeenCalledWith('Settings pressed');

      consoleSpy.mockRestore();
    });

    it('should not throw when history button is pressed', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      const { getByTestId } = renderWithProvider(<MeetingCoachScreen />);

      const historyButton = getByTestId('history-button');
      expect(() => fireEvent.press(historyButton)).not.toThrow();
      expect(consoleSpy).toHaveBeenCalledWith('History pressed');

      consoleSpy.mockRestore();
    });
  });
});
