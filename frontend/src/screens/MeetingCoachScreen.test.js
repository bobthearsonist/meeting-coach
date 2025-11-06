import React from 'react';
import {render} from '@testing-library/react-native';
import MeetingCoachScreen from './MeetingCoachScreen';
import {MeetingProvider} from '../context/MeetingContext';

describe('MeetingCoachScreen', () => {
  // Wrapper component to provide MeetingContext
  const renderWithProvider = component => {
    return render(<MeetingProvider>{component}</MeetingProvider>);
  };

  it('renders without crashing', () => {
    const {getByText} = renderWithProvider(<MeetingCoachScreen />);

    // Verify main sections are rendered
    expect(getByText('📊 Current Status')).toBeTruthy();
    expect(getByText('📈 Emotional Timeline')).toBeTruthy();
  });

  it('displays status dashboard', () => {
    const {getByText} = renderWithProvider(<MeetingCoachScreen />);

    expect(getByText('📊 Current Status')).toBeTruthy();
    expect(getByText('Emotional State')).toBeTruthy();
    expect(getByText('Social Cues')).toBeTruthy();
    expect(getByText('Confidence')).toBeTruthy();
    expect(getByText('Speech Pace')).toBeTruthy();
  });

  it('displays emotional timeline', () => {
    const {getByText} = renderWithProvider(<MeetingCoachScreen />);

    expect(getByText('📈 Emotional Timeline')).toBeTruthy();
    expect(getByText('Last 5 minutes')).toBeTruthy();
  });

  it('displays recent activity feed', () => {
    const {getByText} = renderWithProvider(<MeetingCoachScreen />);

    expect(getByText('💬 Recent Activity')).toBeTruthy();
  });

  it('displays session stats footer', () => {
    const {getByText} = renderWithProvider(<MeetingCoachScreen />);

    expect(getByText(/Duration:/)).toBeTruthy();
    expect(getByText(/Analyses:/)).toBeTruthy();
    expect(getByText(/Alerts:/)).toBeTruthy();
  });

  it('displays recording indicator', () => {
    const {getByText} = renderWithProvider(<MeetingCoachScreen />);

    // Should display connection status (defaults to "Offline" in tests)
    expect(getByText('Offline')).toBeTruthy();
  });

  it('displays success alert when no issues', () => {
    const {getByText} = renderWithProvider(<MeetingCoachScreen />);

    expect(getByText('All good – no alerts')).toBeTruthy();
  });

  // Button interaction tests
  describe('Button Interactions', () => {
    it('should display drawer with settings and history buttons when expanded', () => {
      const {getByLabelText} = renderWithProvider(<MeetingCoachScreen />);

      // Find the drawer toggle button
      const drawerToggle = getByLabelText('Expand drawer');
      expect(drawerToggle).toBeTruthy();

      // The buttons exist in the DOM (even if hidden when collapsed)
      const settingsButton = getByLabelText('Open settings');
      const historyButton = getByLabelText('View history');
      expect(settingsButton).toBeTruthy();
      expect(historyButton).toBeTruthy();
    });
  });
});
