import React from 'react';
import {render} from '@testing-library/react-native';
import SessionStats from './SessionStats';

describe('SessionStats', () => {
  it('renders the component', () => {
    const {getByText} = render(<SessionStats />);
    expect(getByText(/Duration:/)).toBeTruthy();
  });

  it('displays duration stat', () => {
    const {getByText} = render(<SessionStats />);
    expect(getByText(/Duration:/)).toBeTruthy();
    expect(getByText(/3.1 min/)).toBeTruthy();
  });

  it('displays analyses count', () => {
    const {getByText} = render(<SessionStats />);
    expect(getByText(/Analyses:/)).toBeTruthy();
    expect(getByText(/14/)).toBeTruthy();
  });

  it('displays alerts count', () => {
    const {getByText} = render(<SessionStats />);
    expect(getByText(/Alerts:/)).toBeTruthy();
    expect(getByText(/0/)).toBeTruthy();
  });

  it('displays emotion distribution', () => {
    const {getByText} = render(<SessionStats />);
    expect(getByText(/calm: 43%/)).toBeTruthy();
    expect(getByText(/neutral: 36%/)).toBeTruthy();
    expect(getByText(/engaged: 21%/)).toBeTruthy();
  });

  it('renders all three stats in the top row', () => {
    const {getByText} = render(<SessionStats />);
    expect(getByText(/Duration:/)).toBeTruthy();
    expect(getByText(/Analyses:/)).toBeTruthy();
    expect(getByText(/Alerts:/)).toBeTruthy();
  });

  it('renders all three emotion percentages in the bottom row', () => {
    const {getByText} = render(<SessionStats />);
    expect(getByText(/calm: 43%/)).toBeTruthy();
    expect(getByText(/neutral: 36%/)).toBeTruthy();
    expect(getByText(/engaged: 21%/)).toBeTruthy();
  });
});
