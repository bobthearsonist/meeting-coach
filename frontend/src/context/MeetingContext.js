import React, { createContext, useReducer } from 'react';
import * as actionTypes from './actionTypes';

// Initial state for the meeting context
const initialState = {
  emotionalState: 'neutral',
  wpm: 0,
  alerts: [],
  isConnected: false,
  isSessionActive: false,
  isRecording: false,
  timeline: {
    summary: null,
    recentEntries: [],
  },
};

// Create the MeetingContext
const MeetingContext = createContext();

// Reducer function to handle state updates
const meetingReducer = (state, action) => {
  switch (action.type) {
    case actionTypes.UPDATE_EMOTION:
      return { ...state, emotionalState: action.payload };
    case actionTypes.UPDATE_WPM:
      return { ...state, wpm: action.payload };
    case actionTypes.SET_CONNECTION_STATUS:
      return { ...state, isConnected: action.payload };
    case actionTypes.SET_SESSION_STATUS:
      return { ...state, isSessionActive: action.payload };
    case actionTypes.SET_RECORDING_STATUS:
      return { ...state, isRecording: action.payload };
    case actionTypes.ADD_ALERT:
      return { ...state, alerts: [...state.alerts, action.payload] };
    case actionTypes.UPDATE_TIMELINE:
      return { 
        ...state, 
        timeline: {
          summary: action.payload.summary,
          recentEntries: action.payload.recent_entries || [],
        }
      };
    default:
      return state;
  }
};

// Provider component to wrap the app and provide state
export const MeetingProvider = ({ children }) => {
  const [state, dispatch] = useReducer(meetingReducer, initialState);
  return (
    <MeetingContext.Provider value={{ state, dispatch }}>
      {children}
    </MeetingContext.Provider>
  );
};

export default MeetingContext;
