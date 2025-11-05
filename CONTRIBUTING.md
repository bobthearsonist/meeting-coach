# Contributing to Meeting Coach

Thank you for your interest in contributing to Meeting Coach! This document provides guidelines and information for contributors.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/meeting-coach.git`
3. Set up the development environment: `make install`
4. Create a new branch: `git checkout -b feature/your-feature-name`

## 🧪 Testing Requirements

All contributions must include appropriate tests and pass all existing tests.

### Running Tests

Before submitting a pull request, ensure all tests pass:

```bash
# Run all tests
make test

# Run specific test suites
make backend-test        # Backend tests
make frontend-test       # Frontend tests
make test-fast           # Quick feedback during development
```

### Test Organization

**Backend Tests:**
- **Unit Tests** (`tests/unit/`): Test individual modules in isolation
  - Fast, no external dependencies
  - Mock all I/O operations
  - Example: `test_analyzer.py`, `test_transcriber.py`

- **Integration Tests** (`tests/integration/`): Test component interactions
  - May use mocked external services (Ollama, audio hardware)
  - Test realistic workflows
  - Example: `test_pipeline.py`, `test_full_pipeline.py`

- **System Tests** (`tests/integration/`): End-to-end workflows
  - Run only when external dependencies are available
  - Use markers: `@pytest.mark.requires_ollama`, `@pytest.mark.requires_audio`
  - Example: `test_real_audio_integration.py`

**Frontend Tests:**
- **Unit Tests**: Test utilities, services, and pure functions
  - Colocated with source files (e.g., `websocketService.test.js`)
  - Fast, isolated tests

- **Component Tests**: Test React components
  - Use React Testing Library
  - Test user interactions and rendering
  - Example: `EmotionalTimeline.test.js`

- **Integration Tests**: Test service integration and state management
  - Test WebSocket communication
  - Test Context API and hooks
  - Example: `MeetingContext.test.js`

### Writing Tests

#### Backend Test Example

```python
import pytest

# Unit test
@pytest.mark.unit
def test_analyze_emotional_state():
    analyzer = CommunicationAnalyzer()
    result = analyzer.analyze("I'm feeling great today!")
    assert result.emotional_state == "positive"

# Integration test
@pytest.mark.integration
def test_full_pipeline(mock_transcriber, mock_analyzer):
    pipeline = Pipeline(mock_transcriber, mock_analyzer)
    result = pipeline.process_audio(test_audio)
    assert result.transcription is not None
    assert result.analysis is not None
```

#### Frontend Test Example

```javascript
import { render, screen } from '@testing-library/react-native';
import { StatusPanel } from './StatusPanel';

describe('StatusPanel', () => {
  it('displays emotional state correctly', () => {
    render(<StatusPanel emotionalState="calm" />);
    expect(screen.getByText(/calm/i)).toBeTruthy();
  });
});
```

## 🎨 Code Style

### Python (Backend)

- Follow PEP 8 style guide
- Use Black for formatting: `make backend-format`
- Use isort for import sorting
- Maximum line length: 100 characters
- Use type hints where appropriate

```bash
# Format code
cd backend && make format

# Check linting
cd backend && make lint
```

### JavaScript (Frontend)

- Follow ESLint configuration
- Use Prettier for formatting: `make frontend-format`
- Use meaningful variable names
- Document complex logic

```bash
# Format code
cd frontend && npm run format

# Check linting
cd frontend && npm run lint
```

## 📝 Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```
feat(backend): add real-time emotion detection
fix(frontend): resolve WebSocket reconnection issue
docs: update installation instructions
test(backend): add unit tests for analyzer
ci: add code coverage workflow
```

## 🔄 Pull Request Process

1. **Create a branch** from `develop` (or `main` for hotfixes)
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**
   - Write clean, tested code
   - Follow the code style guidelines
   - Update documentation as needed

3. **Test your changes**
   ```bash
   make test           # All tests
   make lint           # All linting
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(scope): your meaningful commit message"
   ```

5. **Push to your fork**
   ```bash
   git push origin feat/your-feature-name
   ```

6. **Create a Pull Request**
   - Use a clear, descriptive title
   - Fill out the PR template
   - Link related issues
   - Request reviews

### PR Requirements

Your PR will be automatically checked by CI workflows:

- ✅ All tests must pass (unit, integration, component)
- ✅ Code must be properly formatted (Black, isort, Prettier)
- ✅ Linting must pass (pylint, flake8, ESLint)
- ✅ No security vulnerabilities introduced
- ✅ Test coverage should not decrease significantly

### CI Workflow Status

The following workflows will run on your PR:

- **PR Checks**: Quick validation (fast tests, linting)
- **Backend Tests**: Comprehensive backend testing
- **Frontend Tests**: Comprehensive frontend testing
- **Code Quality**: Security scans and quality metrics
- **Test Coverage**: Coverage analysis and reporting

You can see the status of these workflows in your PR. All required checks must pass before merging.

## 🔍 Code Review Guidelines

### For Contributors

- Keep PRs focused and reasonably sized (< 500 lines when possible)
- Respond to review comments promptly
- Make requested changes in new commits (don't force-push)
- Update tests when changing functionality
- Add comments for complex logic

### For Reviewers

- Be constructive and respectful
- Focus on code quality, not personal preferences
- Check for test coverage
- Verify documentation is updated
- Test the changes locally when needed

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps to reproduce the bug
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: OS, Python version, Node.js version
6. **Logs**: Relevant error messages or logs

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check if the feature already exists or is planned
2. Clearly describe the feature and its use case
3. Explain why it would be valuable to users
4. Consider proposing an implementation approach

## 🏗️ Project Architecture

### Backend Architecture

```
backend/
├── main.py                 # Entry point, WebSocket server
├── src/
│   ├── analyzer.py         # AI-powered analysis
│   ├── transcriber.py      # Real-time transcription
│   ├── timeline.py         # State tracking
│   ├── ui/                 # Console UI components
│   └── server/             # WebSocket server
└── tests/                  # Test suite
```

### Frontend Architecture

```
frontend/src/
├── components/             # React components
├── screens/                # Screen components
├── context/                # Context API providers
├── hooks/                  # Custom hooks
├── services/               # API/WebSocket services
└── utils/                  # Utilities and constants
```

## 📚 Resources

- [Backend README](backend/README.md) - Backend architecture and setup
- [Frontend README](frontend/README.md) - Frontend architecture and setup
- [Project Summary](PROJECT_SUMMARY.md) - Comprehensive project overview
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python PEP 8](https://pep8.org/)
- [React Testing Library](https://testing-library.com/react)

## 🤝 Community

- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and best practices
- Celebrate successes together

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 with Commons Clause license.

---

**Thank you for contributing to Meeting Coach!** 🎉
