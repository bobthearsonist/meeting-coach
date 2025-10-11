import { useContext, useCallback } from 'react';
import * as actionTypes from '../context/actionTypes';
import MeetingContext from '../context/MeetingContext';

export const useMeetingData = () => {
  const { state, dispatch } = useContext(MeetingContext);

  const updateEmotionalState = useCallback(
    (newState) => {
      dispatch({ type: actionTypes.UPDATE_EMOTION, payload: newState });
    },
    [dispatch]
  );

  const updateWpm = useCallback(
    (newWpm) => {
      dispatch({ type: actionTypes.UPDATE_WPM, payload: newWpm });
    },
    [dispatch]
  );

  const setConnectionStatus = useCallback(
    (status) => {
      dispatch({ type: actionTypes.SET_CONNECTION_STATUS, payload: status });
    },
    [dispatch]
  );

  const setSessionStatus = useCallback(
    (status) => {
      dispatch({ type: actionTypes.SET_SESSION_STATUS, payload: status });
    },
    [dispatch]
  );

  const setRecordingStatus = useCallback(
    (status) => {
      dispatch({ type: actionTypes.SET_RECORDING_STATUS, payload: status });
    },
    [dispatch]
  );

  const addAlert = useCallback(
    (alert) => {
      dispatch({ type: actionTypes.ADD_ALERT, payload: alert });
    },
    [dispatch]
  );

  return {
    emotionalState: state.emotionalState,
    wpm: state.wpm,
    isConnected: state.isConnected,
    isSessionActive: state.isSessionActive,
    isRecording: state.isRecording,
    alerts: state.alerts,
    updateEmotionalState,
    updateWpm,
    setConnectionStatus,
    setSessionStatus,
    setRecordingStatus,
    addAlert,
  };
};

export default useMeetingData;

/*
  Explanation:
  - The custom hook `useMeetingData` is updated to use action type constants from `actionTypes`.
  - This approach minimizes the risk of errors due to typos in action type strings and centralizes the management of action types.
  - Using a hooks folder is a common pattern in React for encapsulating reusable logic. It helps in organizing code better and promotes reusability across components.
*/
