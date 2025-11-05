# GitHub Actions Quick Reference

A quick reference guide for developers working with GitHub Actions in the Meeting Coach project.

## 🚦 Workflow Status Checks

When you create a pull request, these workflows will run:

| Workflow | Duration | Required | Description |
|----------|----------|----------|-------------|
| **PR Checks** | 3-5 min | ✅ Yes | Fast validation (lint + fast tests) |
| **CI** | 5-8 min | ✅ Yes | Main integration testing |
| **Backend Tests** | 6-10 min | ✅ Yes* | Comprehensive backend tests |
| **Frontend Tests** | 8-12 min | ✅ Yes* | Comprehensive frontend tests |
| **Code Quality** | 4-6 min | ⚠️ No | Security scans and metrics |
| **Coverage** | 5-7 min | ⚠️ No | Coverage analysis and reporting |

_* Only required if backend/frontend files changed_

## 🔍 Checking Workflow Status

### On GitHub

1. Go to your PR page
2. Scroll to the checks section at the bottom
3. Click "Show all checks" to see details
4. Click on a check name to view logs

### Locally Before Pushing

```bash
# Run the same checks that CI will run
make test           # All tests
make lint           # All linting

# Backend only
cd backend
black --check *.py src/ tests/
isort --check-only *.py src/ tests/ --profile=black
pytest tests/unit/ -v -m "unit and not slow"

# Frontend only
cd frontend
npm run lint
npm test -- --watchAll=false
```

## 🐛 Common Workflow Failures

### "Black formatting check failed"

**Problem**: Code is not formatted with Black

**Fix**:
```bash
cd backend
make format
git add .
git commit -m "style: format code with black"
```

### "ESLint errors found"

**Problem**: JavaScript linting errors

**Fix**:
```bash
cd frontend
npm run lint --fix
git add .
git commit -m "style: fix linting errors"
```

### "Unit tests failed"

**Problem**: Tests are failing

**Fix**:
1. Run tests locally to see the error
2. Fix the failing tests
3. Re-run to verify

```bash
# Backend
cd backend
pytest tests/unit/ -v -x  # Stop on first failure

# Frontend
cd frontend
npm test -- --watchAll=false --verbose
```

### "Coverage decreased"

**Problem**: Test coverage dropped

**Fix**: This is a warning, not a failure. Add tests if needed:
```bash
# Check what's not covered
cd backend
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### "Workflow timeout"

**Problem**: Workflow took too long

**Fix**: 
- Check for infinite loops or hanging tests
- Mock external dependencies (Ollama, audio devices)
- Mark slow tests with `@pytest.mark.slow`

## 📊 Understanding Artifacts

Workflows generate downloadable artifacts for debugging:

### Coverage Reports
- **Where**: Actions tab → Workflow run → Artifacts
- **What**: HTML coverage reports showing tested/untested code
- **Retention**: 14 days
- **Use**: Identify untested code paths

### Security Reports
- **Where**: Actions tab → Workflow run → Artifacts
- **What**: JSON reports from safety, bandit, npm audit
- **Retention**: 30 days
- **Use**: Review security vulnerabilities

### Quality Reports
- **Where**: Actions tab → Workflow run → Artifacts
- **What**: Pylint, radon, ESLint output
- **Retention**: 30 days
- **Use**: Code quality metrics

## 🔄 Re-running Workflows

### Re-run Failed Jobs Only

1. Go to Actions tab
2. Click on the failed workflow run
3. Click "Re-run failed jobs"

### Re-run All Jobs

1. Go to Actions tab
2. Click on the workflow run
3. Click "Re-run all jobs"

### Trigger Manually

1. Go to Actions tab
2. Click on a workflow (e.g., "CI")
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

## 🎯 Test Markers (Backend)

Use pytest markers to control which tests run:

```python
@pytest.mark.unit  # Fast, isolated unit tests
@pytest.mark.integration  # Component interaction tests
@pytest.mark.slow  # Long-running tests
@pytest.mark.requires_ollama  # Needs Ollama LLM
@pytest.mark.requires_audio  # Needs audio hardware
```

Run specific markers:
```bash
pytest -m "unit"  # Only unit tests
pytest -m "not slow"  # Exclude slow tests
pytest -m "unit and not slow"  # Fast unit tests only
```

## 📝 Conventional Commits

PR titles should follow conventional commits format:

```
feat(scope): add new feature
fix(scope): resolve bug
docs: update documentation
style: format code
refactor: restructure code
test: add tests
chore: maintenance
ci: workflow changes
```

**Examples**:
- `feat(backend): add emotion detection`
- `fix(frontend): resolve WebSocket reconnection`
- `test(backend): add analyzer unit tests`
- `ci: update workflow timeout`

## 🛠️ Workflow Modification

### Adding a New Test

1. Add test file (e.g., `test_new_feature.py`)
2. Mark appropriately (`@pytest.mark.unit`)
3. Workflows auto-detect new tests
4. No workflow changes needed

### Changing Test Configuration

Edit `pytest.ini` (backend) or `package.json` (frontend):

```ini
# backend/pytest.ini
[tool:pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    your_new_marker: Description
```

### Changing Workflow Triggers

Edit workflow file `.github/workflows/*.yml`:

```yaml
on:
  push:
    branches: [ main, develop ]
    paths:  # Only run on specific changes
      - 'backend/**'
      - '.github/workflows/backend-tests.yml'
```

## 🔐 Secrets and Environment Variables

Workflows can access repository secrets:

```yaml
- name: Upload to service
  env:
    API_TOKEN: ${{ secrets.API_TOKEN }}
```

Add secrets in: Settings → Secrets and variables → Actions

## 📈 Performance Tips

### Speed Up Workflow Runs

1. **Use caching**: Workflows cache pip/npm packages automatically
2. **Run in parallel**: Backend and frontend tests run simultaneously
3. **Fail fast**: Use `-x` flag for pytest during development
4. **Skip slow tests**: Mark tests with `@pytest.mark.slow`
5. **Mock dependencies**: Don't require Ollama/audio in CI

### Reduce Costs

1. **Cancel in-progress runs**: Workflows auto-cancel on new commits
2. **Use path filters**: Only run when relevant files change
3. **Limit matrix**: Only test necessary Node.js/Python versions
4. **Set timeouts**: Prevent runaway workflows

## 🆘 Getting Help

### Workflow Logs

View detailed logs:
1. Go to Actions tab
2. Click workflow run
3. Click job name
4. Expand steps to see output

### Debug Mode

Enable debug logging:
1. Settings → Secrets and variables → Actions
2. Add secret: `ACTIONS_STEP_DEBUG = true`
3. Re-run workflow

### Local Debugging

Use act to run workflows locally:
```bash
brew install act
act pull_request  # Simulate PR event
```

### Ask for Help

If workflows fail mysteriously:
1. Check workflow logs
2. Download artifacts
3. Try to reproduce locally
4. Open an issue with logs

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [WORKFLOWS.md](.github/WORKFLOWS.md) - Detailed workflow documentation
- [WORKFLOW_ARCHITECTURE.md](.github/WORKFLOW_ARCHITECTURE.md) - Visual workflow diagrams
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

## 🎓 Best Practices

1. ✅ **Test locally first**: Run `make test` and `make lint` before pushing
2. ✅ **Write fast tests**: Keep unit tests under 1 second each
3. ✅ **Mock external dependencies**: Don't require Ollama/audio in tests
4. ✅ **Use appropriate markers**: Mark tests correctly
5. ✅ **Keep PRs small**: Easier to review and test
6. ✅ **Fix failures quickly**: Don't let broken tests accumulate
7. ✅ **Review artifacts**: Download coverage reports to see gaps
8. ✅ **Follow conventions**: Use conventional commits

---

**Quick Commands Cheat Sheet**

```bash
# Before committing
make test          # Run all tests
make lint          # Run all linting
make format        # Format all code

# Backend only
cd backend
make test-fast     # Quick tests
make test-unit     # Unit tests only
make lint          # Lint Python
make format        # Format Python

# Frontend only
cd frontend
npm test           # Run tests
npm run lint       # Lint JavaScript
npm run format     # Format JavaScript

# View coverage
cd backend && make test-coverage
cd frontend && npm test -- --coverage
```
