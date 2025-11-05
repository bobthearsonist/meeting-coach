# GitHub Actions Workflow Architecture

This document provides a visual overview of the GitHub Actions workflow architecture for the Meeting Coach project.

## Workflow Trigger Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         Trigger Events                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ├─── Push to main/develop
                              │    ├── ci.yml
                              │    ├── backend-tests.yml (backend/** changes)
                              │    ├── frontend-tests.yml (frontend/** changes)
                              │    ├── code-quality.yml
                              │    └── coverage.yml
                              │
                              ├─── Pull Request
                              │    ├── ci.yml
                              │    ├── backend-tests.yml (backend/** changes)
                              │    ├── frontend-tests.yml (frontend/** changes)
                              │    ├── pr-checks.yml
                              │    ├── code-quality.yml
                              │    └── coverage.yml
                              │
                              ├─── Weekly Schedule (Monday 9 AM UTC)
                              │    └── code-quality.yml
                              │
                              └─── Manual Dispatch
                                   ├── ci.yml
                                   ├── backend-tests.yml
                                   ├── frontend-tests.yml
                                   ├── code-quality.yml
                                   └── coverage.yml
```

## Main CI Workflow (`ci.yml`)

```
┌─────────────────────────────────────────────────────────────────┐
│                            CI Workflow                          │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
    ┌─────────▼─────────┐         ┌─────────▼─────────┐
    │  Backend Pipeline │         │ Frontend Pipeline │
    └─────────┬─────────┘         └─────────┬─────────┘
              │                               │
      ┌───────┼───────┐               ┌───────┼───────┐
      ▼       ▼       ▼               ▼       ▼       ▼
   ┌────┐ ┌────┐ ┌────┐           ┌────┐ ┌────┐ ┌────┐
   │Lint│ │Unit│ │Int │           │Lint│ │Unit│ │Int │
   └──┬─┘ └──┬─┘ └──┬─┘           └──┬─┘ └──┬─┘ └──┬─┘
      │      │      │                 │      │      │
      └──────┴──────┘                 └──────┴──────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
                      ┌───────────────┐
                      │  CI Success   │
                      │   (Summary)   │
                      └───────────────┘
```

## Backend Tests Workflow (`backend-tests.yml`)

```
┌─────────────────────────────────────────────────────────────────┐
│                      Backend Tests Workflow                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │  Setup   │
                        │  & Lint  │
                        └────┬─────┘
                             │
                             ▼
                      ┌─────────────┐
                      │ Unit Tests  │
                      │ (Python 3.12)│
                      │             │
                      │ • Unit only │
                      │ • Coverage  │
                      │ • Codecov   │
                      └──────┬──────┘
                             │
                             ▼
                   ┌──────────────────┐
                   │Integration Tests │
                   │                  │
                   │ • Fast tests     │
                   │ • No external    │
                   │   dependencies   │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  System Tests   │
                   │ (main/manual)   │
                   │                 │
                   │ • Full pipeline │
                   │ • Mocked deps   │
                   │ • Optional      │
                   └────────┬────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │Test Summary   │
                    └───────────────┘
```

## Frontend Tests Workflow (`frontend-tests.yml`)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend Tests Workflow                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │  Setup   │
                        │  & Lint  │
                        └────┬─────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Unit Tests    │
                    │  (Node 18, 20)  │
                    │                 │
                    │ • Jest tests    │
                    │ • Coverage      │
                    │ • Codecov       │
                    └────────┬────────┘
                             │
                             ▼
                   ┌──────────────────┐
                   │ Component Tests  │
                   │                  │
                   │ • React Testing  │
                   │   Library        │
                   │ • Components/    │
                   │ • Screens/       │
                   └────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │Integration Tests  │
                  │                   │
                  │ • WebSocket       │
                  │ • Context API     │
                  │ • State mgmt      │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │   Build Test      │
                  │ (main branch)     │
                  │                   │
                  │ • macOS build     │
                  │ • CocoaPods       │
                  └─────────┬─────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │Test Summary   │
                    └───────────────┘
```

## PR Checks Workflow (`pr-checks.yml`)

```
┌─────────────────────────────────────────────────────────────────┐
│                      PR Checks Workflow                         │
│                    (Fast Validation)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                      ┌───────────────┐
                      │Detect Changes │
                      │ (paths-filter)│
                      └───┬───────┬───┘
                          │       │
              ┌───────────┘       └───────────┐
              │                               │
    ┌─────────▼─────────┐         ┌─────────▼─────────┐
    │ Backend Quick     │         │Frontend Quick     │
    │    Check          │         │    Check          │
    │ (if backend/*)    │         │ (if frontend/*)   │
    │                   │         │                   │
    │ • Format check    │         │ • ESLint          │
    │ • Fast tests (-x) │         │ • Fast tests      │
    └─────────┬─────────┘         └─────────┬─────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
         ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
         │PR Size  │    │PR Title │    │Summary  │
         │ Check   │    │ Check   │    │         │
         └─────────┘    └─────────┘    └─────────┘
```

## Code Quality Workflow (`code-quality.yml`)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Code Quality Workflow                        │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
    ┌─────────▼─────────┐         ┌─────────▼─────────┐
    │  Backend Quality  │         │ Frontend Quality  │
    └─────────┬─────────┘         └─────────┬─────────┘
              │                               │
      ┌───────┼───────┐               ┌───────┼───────┐
      ▼       ▼       ▼               ▼       ▼       ▼
   ┌────┐ ┌────┐ ┌────┐           ┌────┐ ┌────┐ ┌────┐
   │Safe│ │Band│ │Qual│           │Audit│ │ES  │ │Dep │
   │ty  │ │it  │ │ity│           │     │ │Lint│ │Rev │
   └────┘ └────┘ └────┘           └─────┘ └────┘ └────┘
     │      │      │                 │       │      │
     └──────┴──────┘                 └───────┴──────┘
            │                               │
            └───────────────┬───────────────┘
                            ▼
                    ┌───────────────┐
                    │Quality Summary│
                    └───────────────┘
```

## Test Coverage Workflow (`coverage.yml`)

```
┌─────────────────────────────────────────────────────────────────┐
│                   Test Coverage Workflow                        │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
    ┌─────────▼─────────┐         ┌─────────▼─────────┐
    │Backend Coverage   │         │Frontend Coverage  │
    │                   │         │                   │
    │ • All tests       │         │ • All tests       │
    │ • Generate badge  │         │ • Generate badge  │
    │ • Upload Codecov  │         │ • Upload Codecov  │
    │ • Comment on PR   │         │ • Comment on PR   │
    │ • HTML report     │         │ • HTML report     │
    └─────────┬─────────┘         └─────────┬─────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
                      ┌───────────────┐
                      │Coverage Summary│
                      └───────────────┘
```

## Workflow Execution Timeline

### Pull Request Flow

```
Time: 0s ──────────────────────────────────────────────────── 15m
     │
     ├─ PR Checks (Fast) ─────────────────────┐ (3-5 min)
     │                                          │
     ├─ CI Workflow ──────────────────────────────┐ (5-8 min)
     │                                              │
     ├─ Backend Tests ─────────────────────────────────┐ (6-10 min)
     │                                                   │
     ├─ Frontend Tests ────────────────────────────────────┐ (8-12 min)
     │                                                       │
     ├─ Code Quality ──────────────────────────────┐ (4-6 min)
     │                                               │
     └─ Coverage ─────────────────────────────────────┐ (5-7 min)
                                                       │
                                                       ▼
                                             All checks complete
```

### Push to Main Flow

```
Time: 0s ──────────────────────────────────────────────────── 20m
     │
     ├─ CI Workflow ──────────────────────────┐ (5-8 min)
     │                                          │
     ├─ Backend Tests ──────────────────────────────┐ (6-10 min)
     │  (includes system tests)                      │
     │                                                │
     ├─ Frontend Tests ─────────────────────────────────┐ (10-15 min)
     │  (includes build verification)                   │
     │                                                   │
     ├─ Code Quality ──────────────────────────┐ (4-6 min)
     │                                           │
     └─ Coverage ─────────────────────────────────┐ (5-7 min)
                                                   │
                                                   ▼
                                         All checks complete
```

## Test Organization

```
Backend Tests:
├── Unit Tests (fast, isolated)
│   ├── test_analyzer.py
│   ├── test_transcriber.py
│   ├── test_dashboard.py
│   └── test_audio_capture.py
│
├── Integration Tests (component interaction)
│   ├── test_pipeline.py
│   ├── test_full_pipeline.py
│   └── test_overly_critical_integration.py
│
└── System Tests (end-to-end, mocked)
    └── test_real_audio_functionality.py (requires_audio)

Frontend Tests:
├── Unit Tests (utilities, services)
│   └── services/websocketService.test.js
│
├── Component Tests (React components)
│   ├── components/EmotionalTimeline.test.js
│   ├── components/SessionStats.test.js
│   ├── components/ActivityFeed.test.js
│   └── components/StatusPanel.test.js
│
└── Integration Tests (WebSocket, Context)
    ├── context/MeetingContext.test.js
    └── screens/MeetingCoachScreen.test.js
```

## Success Criteria

### Required for PR Merge

- ✅ **PR Checks**: Backend/Frontend quick checks (if changes detected)
- ✅ **CI Success**: All lint and test jobs pass
- ✅ **Backend Unit Tests**: All unit tests pass
- ✅ **Frontend Unit Tests**: All unit tests pass

### Optional (Non-Blocking)

- ⚠️ **Code Quality**: Security and quality metrics (continue on error)
- ⚠️ **Coverage**: Coverage reporting (informational)
- ⚠️ **Build Test**: macOS build (main branch only)

## Artifacts & Reports

```
Workflow Artifacts:
├── Coverage Reports (14 days)
│   ├── backend-coverage-report (HTML)
│   └── frontend-coverage-report (HTML)
│
├── Security Reports (30 days)
│   ├── backend-security-reports (JSON)
│   └── frontend-security-reports (JSON)
│
└── Quality Reports (30 days)
    ├── backend-quality-reports (JSON)
    └── frontend-quality-reports (JSON)

External Integrations:
├── Codecov (coverage tracking)
├── GitHub PR Comments (coverage %)
└── Status Checks (branch protection)
```

## Optimization Features

1. **Concurrency Control**: Cancel in-progress runs on new commits
2. **Path Filtering**: Only run relevant tests based on changed files
3. **Dependency Caching**: Cache pip and npm packages
4. **Parallel Execution**: Backend and frontend tests run simultaneously
5. **Matrix Testing**: Test against multiple Node.js/Python versions
6. **Fail Fast**: PR checks stop on first error for quick feedback
7. **Conditional Jobs**: System tests and builds only on main/manual

---

**Legend:**
- `┌─┐` Workflow/Job
- `│` Sequential execution
- `├─┤` Parallel execution
- `▼` Dependency relationship
- `✅` Required check
- `⚠️` Optional check
