# Meeting Coach Project - Complete Guide

## 🚀 SESSION RESTART PROMPT

**Copy/paste this into new sessions to quickly resume:**

---

**Context:** I'm working on a Meeting Coach project - a real-time communication analysis system for neurodivergent individuals. This is a learning exercise to understand professional React patterns through component-by-component implementation.

**Project Status:**

**Backend (✅ COMPLETE):** Python WebSocket server with real-time audio transcription (RealtimeSTT), LLM emotional analysis (Ollama llama2), broadcasting engine. Working console client as reference implementation. Files: `backend/main.py` (server), `backend/console_client.py` (client).

**Frontend (🔄 IN PROGRESS):** React Native 0.73.11 project with macOS support. Theme system complete (`frontend/src/utils/theme.js`), constants complete (`frontend/src/utils/constants.js`), WebSocket service layer implemented with `reconnecting-websocket` (`frontend/src/services/websocketService.js` + unit tests), ✅ **coarse-grained screen layout extracted** (`frontend/src/screens/MeetingCoachScreen.jsx` + tests), ✅ **Jest testing configured** with colocated test pattern, ✅ **State management implemented** (Context API + custom hooks + action types), ✅ **Real-time WebSocket integration complete** - UI now receives live backend updates, ready to split into focused subcomponents.

**Architecture:**

```text
Python Backend (WebSocket Server: ws://localhost:8000)
    ↓ Real-time JSON messages
React Native App (Mobile Client)
  ├── WebSocket Service Layer ✅
  ├── Screen Layout (Coarse) ✅
  ├── Context + State Management ✅
  ├── Custom Hooks (useMeetingData) ✅
  ├── Real-time WebSocket Integration ✅
  ├── Component Extraction (Fine-grained) ← NEXT STEP
  └── UI Components (Real-time Updates)
```

**Learning Goals:** Professional React patterns (service layer, Context API, custom hooks), real-time WebSocket integration, component composition and state management, theme system and design consistency.

**Current Task:** Extract focused subcomponents from `MeetingCoachScreen.jsx` - starting with StatusPanel (emotional state, social cues, confidence, speech pace).

**To Test Backend:**

```bash
cd backend && python main.py  # Terminal 1
cd backend && python console_client.py  # Terminal 2
# Then speak into microphone to see real-time updates
```

**Next Steps:**

1. Extract StatusPanel component (emotional state, social cues, confidence, speech pace)
2. Extract EmotionalTimeline component (timeline visualization)
3. Extract ActivityFeed component (transcript items)
4. Extract SessionStats component (footer stats)
5. **Add Navigation** (optional learning exercise)
   - Install React Navigation dependencies
   - Create AppNavigator with Stack Navigator
   - Demonstrates navigation pattern for future screens (Settings, History, Onboarding)

**TODO:**

- Convert `commonStyles.section` to a `<Section>` wrapper component for dynamic theming (dark/light mode support)
- Add ThemeContext for managing dark/light themes (future enhancement)

---

## 📋 PROJECT OVERVIEW

A real-time communication analysis and coaching system for neurodivergent individuals, featuring audio transcription, LLM emotional analysis, and WebSocket-based real-time updates.

## Educational Goals

This project is designed as a **learning exercise** to understand professional React patterns:

- **Component-by-component implementation** to learn React concepts incrementally
- **Professional architecture patterns** from the start (no shortcuts)
- **Service layer pattern** for backend integration
- **State management** with Context API and custom hooks
- **Real-time WebSocket integration**
- **Theme system and design consistency**

## Current Architecture

### Backend (✅ COMPLETE)

```
┌─────────────────────────────────────────────────────────┐
│                    Backend System                       │
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │         MeetingCoach Engine (main.py)          │   │
│  │                                                 │   │
│  │  RealtimeSTT → Analyzer → Timeline             │   │
│  │  (Audio)       (LLM)       (State)              │   │
│  │                                                 │   │
│  │               ↓ Broadcast                       │   │
│  │                                                 │   │
│  │  WebSocket Server (ws://localhost:8000)        │   │
│  └────────────────────────────────────────────────┘   │
│                       ↓                                │
│      ┌────────────────┴─────────────────┐             │
│      ↓                                  ↓             │
│  Console Client                   React Native App    │
│  (console_client.py) ✅           (frontend/) 🔄      │
└─────────────────────────────────────────────────────────┘
```

**Key Components:**

- `main.py` - WebSocket server + MeetingCoach engine
- `ws_server.py` - WebSocket server implementation
- `console_client.py` - Console WebSocket client (working reference)
- `analyzer.py` - LLM communication analysis
- `transcriber.py` - RealtimeSTT wrapper
- `timeline.py` - State tracking & history

**Technology Stack:**

- **RealtimeSTT** - Real-time speech-to-text
- **Ollama (llama2)** - Local LLM for emotion analysis
- **websockets 15.0.1** - Real-time communication
- **Python asyncio** - Concurrent client management

**Client Implementation:**

- **reconnecting-websocket** - Resilient WebSocket client for React Native with auto-retry and status introspection

### Frontend (🔄 IN PROGRESS)

**Platform:** React Native 0.73.11 + React 18.2.0

**Completed:**

- ✅ Project setup with macOS support
- ✅ Theme system (`frontend/src/utils/theme.js`) - Centralized design tokens with complete emotional state colors
- ✅ Constants (`frontend/src/utils/constants.js`) - App-wide configuration
- ✅ WebSocket service layer with reconnecting-websocket + Jest tests (`frontend/src/services/websocketService.js`)
- ✅ Screen extraction (`frontend/src/screens/MeetingCoachScreen.jsx`) - Coarse-grained layout ready for component breakdown
- ✅ Jest testing setup with React Native preset and colocated test pattern
- ✅ State management - MeetingContext with useReducer pattern (`frontend/src/context/MeetingContext.js`)
- ✅ Action types centralized (`frontend/src/context/actionTypes.js`)
- ✅ Custom hook - useMeetingData (`frontend/src/hooks/useMeetingData.js`)
- ✅ Real-time WebSocket integration - Screen subscribes to backend events and updates state
- ✅ Connection status tracking (WebSocket, session, recording states)

**Next Steps (Learning Goals):**

- 🔄 Component Extraction (split screen → focused subcomponents: StatusPanel, EmotionalTimeline, ActivityFeed, SessionStats)

## Key Design Decisions

### 1. WebSocket Architecture

**Chosen over HTTP/SSE/gRPC for:**

- Bidirectional real-time communication
- Low latency (<100ms updates)
- Multiple concurrent client support
- Clean separation: backend broadcasts, clients display

### 2. Single Backend Mode

**Refactored from dual console modes to WebSocket-only:**

- Eliminates code duplication
- One engine, multiple client types
- Console dashboard is now a WebSocket client

### 3. Learning-First Approach

**Professional patterns from the start:**

- Service layer for API abstraction
- Context + custom hooks for state management
- Theme system for design consistency
- Component composition patterns

## WebSocket Protocol

### Server → Client Messages

**`meeting_update` - Full State**

```json
{
  "type": "meeting_update",
  "emotional_state": "calm",
  "social_cue": "appropriate",
  "confidence": 0.9,
  "wpm": 150,
  "text": "transcribed speech",
  "coaching": "Great pace!",
  "timestamp": 1696598400.123
}
```

**Other Message Types:**

- `transcription` - New speech detected
- `emotion_update` - Emotional state changed
- `alert` - Coaching alert
- `session_status` - Session started/stopped
- `recording_status` - Microphone listening state

### Client → Server Messages

```json
{"type": "start_session"}
{"type": "stop_session"}
{"type": "ping"}
```

## How to Test Current System

### Backend Testing

```bash
cd backend
python main.py             # Start WebSocket server
python console_client.py   # Connect console client
```

### Frontend Testing

```bash
cd frontend
npm test                   # Run Jest suites (includes WebSocket service)
```

## Learning Journey Roadmap

### Phase 1: Service Layer (✅ COMPLETE)

**Goal:** Learn professional API integration patterns

**What You Built:**

- Minimal WebSocket wrapper around `reconnecting-websocket`
- Event subscription system (`subscribe`, `onStatusChange`)
- JSON parsing and error propagation helpers
- Deterministic test helpers (`__reset`) for Jest

**Key Learnings:**

- Service layer pattern keeps UI decoupled from network concerns
- Leaning on a proven client library reduces boilerplate and bugs
- Connection status snapshots make it easy to power future hooks/context
- Tests are simpler when the service exposes a narrow surface area

**Implementation Highlights:**

```javascript
// frontend/src/services/websocketService.js
import websocketService, { connect, subscribe, onStatusChange } from './websocketService';

await connect();

const unsubscribe = subscribe('meeting_update', (payload) => {
  // Handle real-time data from the backend
});

const stopStatus = onStatusChange(({ status }) => {
  console.log('Connection status:', status);
});

// Clean up when the component unmounts
unsubscribe();
stopStatus();
websocketService.disconnect();
```

**Verification:** `npm test` runs Jest suites covering happy paths, reconnection states, and JSON parsing edge cases.

**Why This Matters:** Service layers create clean separation between UI and data, making code testable and maintainable.

### Phase 3: State Management (✅ COMPLETE)

**Goal:** Learn modern React state patterns

**What You Built:**

- Created `MeetingContext` with Provider component using useReducer
- Centralized action types in `actionTypes.js` for consistency
- Built `useMeetingData` custom hook to access state and actions
- Integrated real-time WebSocket subscriptions with state updates
- Tracked multiple state types: emotional state, WPM, connection status, session status, recording status

**Key Learnings:**

- Context API provides dependency injection for React
- useReducer scales better than useState for complex state
- Action types as constants prevent typos and enable refactoring
- Custom hooks create clean interfaces for state access
- Subscription pattern with cleanup functions prevents memory leaks

**Implementation Highlights:**

```javascript
// MeetingContext.js - Provider wraps app
export const MeetingProvider = ({ children }) => {
  const [state, dispatch] = useReducer(meetingReducer, initialState);
  return (
    <MeetingContext.Provider value={{ state, dispatch }}>
      {children}
    </MeetingContext.Provider>
  );
};

// useMeetingData.js - Custom hook for components
export const useMeetingData = () => {
  const { state, dispatch } = useContext(MeetingContext);

  const updateEmotionalState = useCallback(
    (newState) => dispatch({ type: actionTypes.UPDATE_EMOTION, payload: newState }),
    [dispatch]
  );

  return { emotionalState: state.emotionalState, updateEmotionalState, ... };
};

// Component usage
const { emotionalState, updateEmotionalState } = useMeetingData();
```

**Patterns Demonstrated:**

- **Observer Pattern**: Components automatically re-render on state changes
- **Facade Pattern**: Custom hook simplifies complex state access
- **Command Pattern**: Action objects encapsulate state change requests
- **Singleton Pattern**: Single shared state instance via Context

**Why This Matters:** Modern React apps use Context + hooks instead of props drilling, creating cleaner component hierarchies and easier testing.

### Phase 4: Component Architecture (🚀 IN PROGRESS)

**Goal:** Reshape the monolithic UI into purposeful building blocks

**Tasks:**

- ✅ Create `frontend/src/screens/MeetingCoachScreen.jsx` as the new top-level screen
- ✅ Migrate existing layout from `MeetingCoachUI.jsx` into the screen component
- ✅ Set up Jest testing with React Native preset and colocated test pattern
- 🔄 Identify logical sub-sections (StatusPanel, TranscriptFeed, CoachingTips)
- 🔄 Gradually extract those sections into focused child components
- 🔄 Keep props simple for now; wire data once Context is available

**Concepts:**

- Coarse-to-fine component refactors
- Layout composition and styling reuse
- Separation between screen orchestration and presentational pieces
- Preparing components for future state injection

### Phase 3: State Management

**Goal:** Learn modern React state patterns

**Tasks:**

- Create `frontend/src/context/MeetingContext.js`
- Implement Context + useReducer pattern
- Subscribe to WebSocket service status/data streams
- Manage real-time data updates for UI consumers

**Concepts:**

- Context API
- useReducer vs useState
- State normalization
- Performance optimization

### Phase 4: Custom Hooks

**Goal:** Learn data access abstraction

**Tasks:**

- Create `frontend/src/hooks/useMeetingData.js`
- Encapsulate state access logic
- Provide clean component interface
- Handle loading/error states

**Concepts:**

- Custom hooks pattern
- Data access layer
- Hook composition
- Side effect management

### Phase 5: Navigation & Polish

**Goal:** Complete app with routing

**Tasks:**

- Set up React Navigation
- Add settings screen
- Add session history
- Polish UI/UX

**Concepts:**

- Navigation patterns
- Screen composition
- State persistence
- User experience

## Quick Start Commands

### Backend

```bash
cd backend
make install          # Install dependencies
python main.py        # Start WebSocket server
python console_client.py  # Test with console client
make test             # Run tests
```

### Frontend

```bash
cd frontend
npm install           # Install dependencies
npm run macos         # Start React Native app
npm test              # Run Jest tests (WebSocket service + future suites)
```

## Project Files Structure

```text
teams-meeting-coach/
├── backend/                 # Python WebSocket server (COMPLETE)
│   ├── main.py             # Main entry point
│   ├── ws_server.py        # WebSocket server
│   ├── console_client.py   # Console client
│   ├── analyzer.py         # LLM analysis
│   ├── transcriber.py      # Audio transcription
│   ├── timeline.py         # State tracking
│   ├── dashboard.py        # Console UI
│   ├── tests/              # Test suite
│   └── requirements.txt    # Dependencies
├── frontend/               # React Native app (IN PROGRESS)
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── utils/          # Theme & constants (DONE)
│   │   ├── services/       # API layer (DONE)
│   │   ├── context/        # State management (NEXT)
│   │   └── hooks/          # Custom hooks (NEXT)
│   ├── macos/              # macOS-specific files
│   └── package.json        # Dependencies
├── PROJECT_SUMMARY.md      # This file
└── SESSION_RESTART.md      # Session restart prompt
```

## Development Environment

**Prerequisites:**

- Python 3.12+
- Node.js 18+
- Ollama installed and running
- Microphone access
- Xcode (for macOS/iOS development)

**Key Dependencies:**

- Backend: RealtimeSTT, websockets, ollama
- Frontend: React Native 0.73.11, React Navigation

## Current Status Summary

- ✅ **Backend Architecture:** Complete WebSocket server with real-time audio analysis
- ✅ **Protocol Design:** JSON-based WebSocket messaging protocol
- ✅ **Console Client:** Working reference implementation
- ✅ **Frontend Foundation:** Theme system, project structure
- ✅ **Service Layer:** Reconnecting WebSocket wrapper + tests
- 🚀 **Component Architecture:** Breaking monolithic screen into modules
- 🔄 **State Management:** Context + hooks pattern
- 🔄 **Navigation:** React Navigation setup

## Success Criteria

The project will be complete when:

1. **Technical:** React Native app receives real-time WebSocket updates ✅
2. **Educational:** All major React patterns implemented and understood (in progress)
3. **Functional:** Mobile app displays live transcription and coaching ✅ (needs component refinement)
4. **Architecture:** Clean separation of concerns throughout ✅

---

**Next Session Goal:** Extract StatusPanel component to learn component composition patterns in React.

## 📚 LEARNING GUIDE

### React Native Learning Path

This project teaches professional React patterns through hands-on implementation:

#### Phase 1: Service Layer Pattern ✅ COMPLETE

**What You'll Learn:**

- API abstraction and separation of concerns
- WebSocket lifecycle management (connect, disconnect, reconnect)
- Error handling strategies
- Promise-based and event-driven patterns

**Implementation:**

```javascript
// frontend/src/services/websocketService.js
class WebSocketService {
  connect() {
    /* Connection logic */
  }
  disconnect() {
    /* Cleanup logic */
  }
  sendMessage(data) {
    /* Send to backend */
  }
  onMessage(callback) {
    /* Handle incoming messages */
  }
  onError(callback) {
    /* Error handling */
  }
}
```

**Why This Matters:** Service layers create clean separation between UI and data, making code testable and maintainable.

#### Phase 2: Component Architecture 🚀 IN PROGRESS

**What You'll Learn:**

- Organizing large layouts into purposeful React components
- Designing screen-level orchestrators vs presentational children
- Managing styles and spacing during refactors
- Preparing components for future data dependencies

**Implementation:**

```javascript
// frontend/src/screens/MeetingCoachScreen.jsx
export const MeetingCoachScreen = () => {
  return (
    <SafeAreaView style={styles.container}>
      <StatusPanel />
      <TranscriptFeed />
      <CoachingTips />
    </SafeAreaView>
  );
};
```

**Why This Matters:** Establishing a clean component hierarchy first makes later state and hook integrations straightforward and reduces churn.

#### Phase 3: Context + State Management ✅ COMPLETE

**What You Learned:**

- Context API for global state
- useReducer pattern for complex state management
- Action types as constants for maintainability
- Custom hooks for clean state access
- Real-time state updates from WebSocket events

**Implementation:**

```javascript
// frontend/src/context/MeetingContext.js
const MeetingContext = createContext();

export const MeetingProvider = ({ children }) => {
  const [state, dispatch] = useReducer(meetingReducer, initialState);
  return (
    <MeetingContext.Provider value={{ state, dispatch }}>
      {children}
    </MeetingContext.Provider>
  );
};
```

**Why This Matters:** Modern React apps use Context + hooks instead of props drilling for state management, creating cleaner architectures.

#### Phase 4: Component Architecture 🚀 IN PROGRESS

**What You'll Learn:**

- Context API for global state
- useReducer vs useState patterns
- State normalization techniques
- Performance optimization with React.memo

**Implementation:**

```javascript
// frontend/src/context/MeetingContext.js
const MeetingContext = createContext();

export const MeetingProvider = ({ children }) => {
  const [state, dispatch] = useReducer(meetingReducer, initialState);
  return (
    <MeetingContext.Provider value={{ state, dispatch }}>
      {children}
    </MeetingContext.Provider>
  );
};
```

**Why This Matters:** Modern React apps use Context + hooks instead of props drilling for state management.

#### Phase 4: Custom Hooks Pattern

**What You'll Learn:**

- Data access abstraction
- Hook composition and reusability
- Side effect management with useEffect
- Custom hooks for WebSocket integration

**Implementation:**

```javascript
// frontend/src/hooks/useMeetingData.js
export const useMeetingData = () => {
  const { state, dispatch } = useContext(MeetingContext);

  const updateEmotionalState = useCallback(
    (newState) => {
      dispatch({ type: 'UPDATE_EMOTION', payload: newState });
    },
    [dispatch]
  );

  return {
    emotionalState: state.emotionalState,
    wpm: state.wpm,
    alerts: state.alerts,
    updateEmotionalState,
  };
};
```

**Why This Matters:** Custom hooks encapsulate complex logic and make components clean and focused.

#### Phase 5: Real-Time Integration

**What You'll Learn:**

- Connecting WebSocket data to UI components
- Handling rapid state updates efficiently
- Optimizing re-renders for real-time data
- Error boundaries and graceful degradation

**Integration Pattern:**

```javascript
const StatusDashboard = () => {
  const { emotionalState, wpm, isConnected } = useMeetingData();

  return (
    <View style={styles.dashboard}>
      <EmotionalStateIndicator state={emotionalState} />
      <WPMDisplay value={wpm} />
      <ConnectionStatus connected={isConnected} />
    </View>
  );
};
```

**Why This Matters:** Real-time applications require careful performance consideration and error handling.

### Key React Concepts Covered

1. **Service Layer Pattern** - API abstraction
2. **Context API** - Global state management
3. **Custom Hooks** - Logic reuse and encapsulation
4. **Component Composition** - Building complex UI from simple parts
5. **Performance Optimization** - React.memo, useCallback, useMemo
6. **Error Handling** - Error boundaries and graceful degradation
7. **Theme Systems** - Consistent design implementation
8. **Real-time UI** - WebSocket integration patterns

### Learning Benefits

- **Professional Patterns:** Learn industry-standard React architecture
- **Real-World Skills:** WebSocket integration is common in modern apps
- **Performance Awareness:** Understand React optimization techniques
- **Clean Code:** Separation of concerns and maintainable architecture
- **Testing Foundation:** Service layers and hooks are easily testable

### Success Metrics

You'll know you've succeeded when:

- [x] WebSocket service cleanly abstracts all network communication
- [ ] Context provides clean state management without props drilling
- [ ] Custom hooks encapsulate complex logic and are reusable
- [ ] Components are focused, composable, and easy to understand
- [ ] Real-time updates work smoothly without performance issues
- [ ] Error states are handled gracefully throughout the app

### Next Learning Session

**Goal:** Carve the monolithic UI into a `MeetingCoachScreen` plus first-level child components
**File:** `frontend/src/screens/MeetingCoachScreen.jsx`
**Focus:** Coarse-to-fine component extraction and layout organization
**Outcome:** Screen scaffold ready to accept shared state and future hooks without large refactors

Ready to keep layering professional React patterns on top of the new service foundation!
