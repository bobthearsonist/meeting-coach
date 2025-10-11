import React from 'react';
import { MeetingProvider } from './src/context/MeetingContext';
import MeetingCoachScreen from './src/screens/MeetingCoachScreen';

export default function App() {
  return (
    <MeetingProvider>
      <MeetingCoachScreen />
    </MeetingProvider>
  );
}
