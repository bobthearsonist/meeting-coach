import React from 'react';
import { renderHook, act } from '@testing-library/react-native';
import { MeetingProvider } from './MeetingContext';
import useMeetingData from '../hooks/useMeetingData';
import * as actionTypes from './actionTypes';

describe('MeetingContext', () => {
  const wrapper = ({ children }) => (
    <MeetingProvider>{children}</MeetingProvider>
  );

  it('provides initial state', () => {
    const { result } = renderHook(() => useMeetingData(), { wrapper });

    expect(result.current.emotionalState).toBe('neutral');
    expect(result.current.wpm).toBe(0);
    expect(result.current.isConnected).toBe(false);
    expect(result.current.alerts).toEqual([]);
  });

  it('updates emotional state', () => {
    const { result } = renderHook(() => useMeetingData(), { wrapper });

    act(() => {
      result.current.updateEmotionalState('calm');
    });

    expect(result.current.emotionalState).toBe('calm');
  });

  it('updates WPM', () => {
    const { result } = renderHook(() => useMeetingData(), { wrapper });

    act(() => {
      result.current.updateWpm(150);
    });

    expect(result.current.wpm).toBe(150);
  });

  it('updates connection status', () => {
    const { result } = renderHook(() => useMeetingData(), { wrapper });

    act(() => {
      result.current.setConnectionStatus(true);
    });

    expect(result.current.isConnected).toBe(true);
  });

  it('adds alerts', () => {
    const { result } = renderHook(() => useMeetingData(), { wrapper });

    act(() => {
      result.current.addAlert('Test alert');
    });

    expect(result.current.alerts).toEqual(['Test alert']);

    act(() => {
      result.current.addAlert('Another alert');
    });

    expect(result.current.alerts).toEqual(['Test alert', 'Another alert']);
  });
});
