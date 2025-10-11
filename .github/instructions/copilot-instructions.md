---
applyTo: '**'
---

# Instructions

## Development Workflow

This project uses Python with a virtual environment and Make for task automation.

**Key Guidelines:**

- Use `make` for all development tasks (see README.md Development Setup section)
- Split chained commands over `&&` where feasible (e.g. `npm install && npm test` → separate `npm install` then `npm test`)
- All Python commands should use the virtual environment (handled automatically by Make targets)

## Virtual Environment

The project automatically handles virtual environment activation through:

- Make targets (recommended)
- Shell scripts (`./run_with_venv.sh`, `./run_tests_venv.sh`)
- VS Code settings (`.vscode/settings.json`)
- Python version specification (`.python-version`)

**See the "🛠️ Development Setup" section in README.md for complete details.**

## Frontend Test Structure

**IMPORTANT:** This project uses **colocated tests**, NOT a separate `__tests__` folder.

**Correct test file placement:**
```
frontend/src/components/
  StatusPanel.jsx
  StatusPanel.test.js          ✅ Correct - colocated with component
  EmotionalTimeline.jsx
  EmotionalTimeline.test.js    ✅ Correct - colocated with component

frontend/src/screens/
  MeetingCoachScreen.jsx
  MeetingCoachScreen.test.js   ✅ Correct - colocated with screen
```

**WRONG - Do NOT create:**
```
frontend/src/components/__tests__/StatusPanel.test.js  ❌ WRONG
frontend/src/screens/__tests__/MeetingCoachScreen.test.js  ❌ WRONG
```

**Pattern:** Test files should be in the SAME directory as the file being tested, with `.test.js` suffix.
