import React from 'react';
import {render} from '@testing-library/react-native';
import SessionStats from './SessionStats';
import {MeetingProvider} from '../context/MeetingContext';

// Wrapper to provide MeetingContext
const renderWithProvider = component => {
  return render(<MeetingProvider>{component}</MeetingProvider>);
};

describe('SessionStats', () => {
  it('renders the component', () => {
    const {getByText} = renderWithProvider(<SessionStats />);
    expect(getByText(/Duration:/)).toBeTruthy();
  });

  it('displays duration stat with default value', () => {
    const {getByText} = renderWithProvider(<SessionStats />);
    expect(getByText(/Duration:/)).toBeTruthy();
    expect(getByText(/0\.0 min/)).toBeTruthy();
  });

  it('displays analyses count with default value', () => {
    const {getByText} = renderWithProvider(<SessionStats />);
    expect(getByText(/Analyses:/)).toBeTruthy();
    // The value 0 appears multiple times, just verify the label exists
    expect(getByText('Analyses: 0')).toBeTruthy();
  });

  it('displays alerts count with default value', () => {
    const {getAllByText} = renderWithProvider(<SessionStats />);
    const alertsText = getAllByText(/Alerts:/);
    expect(alertsText.length).toBeGreaterThan(0);
  });

  it('displays no emotion data message when no data available', () => {
    const {getByText} = renderWithProvider(<SessionStats />);
    expect(getByText('No emotion data yet')).toBeTruthy();
  });

  it('renders all three stats in the top row', () => {
    const {getByText} = renderWithProvider(<SessionStats />);
    expect(getByText(/Duration:/)).toBeTruthy();
    expect(getByText(/Analyses:/)).toBeTruthy();
    expect(getByText(/Alerts:/)).toBeTruthy();
  });

  it('displays placeholder when no emotion distribution data', () => {
    const {getByText} = renderWithProvider(<SessionStats />);
    expect(getByText('No emotion data yet')).toBeTruthy();
  });
});
