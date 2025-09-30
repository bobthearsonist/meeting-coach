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
