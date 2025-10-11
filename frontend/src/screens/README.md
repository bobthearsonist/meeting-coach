# Screens

This directory contains the top-level screen components for the Meeting Coach application.

## MeetingCoachScreen

The main screen component that orchestrates the entire Meeting Coach UI. This is a coarse-grained layout that will be progressively refined into focused subcomponents.

### Current Structure

```text
MeetingCoachScreen
├── Header (title, subtitle, recording indicator)
├── Status Dashboard (emotional state, social cues, confidence, speech pace)
├── Emotional Timeline (visualization of emotional states over time)
├── Activity Feed (recent transcripts)
└── Session Stats Footer (duration, analyses, alerts, emotion distribution)
```

### Component Extraction Plan

The screen follows a **coarse-to-fine component extraction strategy**:

1. **Phase 1 (✅ Complete)**: Extract coarse-grained screen layout

   - Move UI from `MeetingCoachUI.jsx` to `MeetingCoachScreen.jsx`
   - Update `App.js` to use the screen component
   - Add basic tests

2. **Phase 2 (🔄 Next)**: Extract focused subcomponents

   - `StatusPanel` - Current status indicators
   - `EmotionalTimeline` - Timeline visualization
   - `ActivityFeed` - Transcript list
   - `SessionStats` - Footer statistics

3. **Phase 3**: Add state management

   - Create `MeetingCoachContext` for shared state
   - Implement custom hooks for data access
   - Wire WebSocket service to components

4. **Phase 4**: Refine granularity
   - Break down subcomponents into smaller pieces as needed
   - Extract reusable UI elements into shared components
   - Add PropTypes/TypeScript definitions

### Testing

Each screen component should have corresponding tests in `__tests__/` directory.

Run tests:

```bash
cd frontend
npm test -- src/screens
```

### Future Screens

As the application grows, additional screens will be added:

- `SettingsScreen` - Configuration and preferences
- `HistoryScreen` - Past session recordings and analysis
- `CalibrationScreen` - Initial setup and voice calibration
