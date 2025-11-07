# Testing Strategy

## Philosophy: Full Regression Testing

This project uses a **full regression testing** approach. All tests run on every commit, regardless of which files changed.

### Why Regression Testing?

**We prioritize reliability over speed.** Running all tests every time provides:

1. **Complete Confidence**: Every commit is validated against the entire test suite
2. **Catch Side Effects**: Changes in one area might affect seemingly unrelated code
3. **Integration Coverage**: Ensures all components work together correctly
4. **Simpler CI**: No complex change detection logic or path filters to maintain
5. **No Surprises**: Never miss a test due to incorrect change detection

### What We DON'T Do

❌ **Selective Testing** - We don't use tools like:
- `pytest-testmon` (only runs tests affected by code changes)
- `jest --onlyChanged` (only runs tests for changed files)
- Path-based filtering in CI workflows
- Manual test selection based on changed files

❌ **Path-Based Filters** - We don't skip test jobs based on:
- Which directories were modified
- File type changes (e.g., skip backend tests if only frontend changed)
- GitHub Actions `paths` filters

### What We DO Instead

✅ **Run Everything**: All tests execute on every push and pull request

✅ **Organize by Type**: Tests are grouped logically for clarity:
- **Backend**: Unit tests, integration tests (fast), integration tests (all)
- **Frontend**: Unit tests, component tests, integration tests

✅ **Parallel Execution**: Jobs run in parallel to minimize total time:
- Backend lint, unit tests, and integration tests run concurrently
- Frontend lint, unit tests, component tests, and integration tests run concurrently
- Coverage jobs run after tests complete

✅ **Smart Markers**: Tests are marked for selective local runs:
- Developers can run `pytest -m unit` locally for fast feedback
- CI always runs the full suite

## Test Organization

### Backend (Python + pytest)

```bash
backend/tests/
├── unit/                    # Fast, isolated unit tests
│   ├── test_analyzer.py
│   ├── test_transcriber.py
│   └── test_dashboard.py
└── integration/             # Integration tests
    ├── test_pipeline.py
    └── test_full_pipeline.py
```

**Markers** (for local development only):
- `unit` - Unit tests (fast, no external dependencies)
- `integration` - Integration tests
- `slow` - Tests that take significant time
- `requires_ollama` - Tests requiring Ollama to be running
- `requires_audio` - Tests requiring audio hardware

**CI Execution**:
- All unit tests run with the `unit` marker
- All integration tests run (fast subset first, then all including slow)

### Frontend (JavaScript + Jest)

```bash
frontend/src/
├── components/
│   └── *.test.js           # Component unit tests
├── services/
│   └── *.test.js           # Service integration tests
└── context/
    └── *.test.js           # State management tests
```

**Test Patterns**:
- `**/*.test.js` - All test files
- `**/components/**/*.test.js` - Component tests
- `**/services/**/*.test.js` - Service tests
- `**/*.integration.test.js` - Integration tests

**CI Execution**:
- All tests run with `npm test` (no filters)
- Component tests run separately for better visibility
- Integration tests run separately

## Local Development Workflow

While CI runs all tests, developers can use markers and filters locally for fast feedback:

### Backend Local Testing

```bash
# Fast feedback during development
pytest -m unit                    # Only unit tests
pytest -m "unit and not slow"     # Fast unit tests only

# Before pushing
make test                         # Run all tests (what CI runs)
make test-coverage                # With coverage report
```

### Frontend Local Testing

```bash
# Fast feedback during development
npm test -- --testPathPattern=components    # Only component tests
npm test -- --testPathPattern=services      # Only service tests

# Before pushing
npm test                          # Run all tests (what CI runs)
npm test -- --coverage            # With coverage report
```

## CI/CD Workflow Details

### CI Workflow (`ci.yml`)

Runs on every push and pull request to `main`:

**Backend Jobs** (parallel):
1. **Lint** - pylint on all Python code
2. **Unit Tests** - All tests marked `unit`
3. **Integration Tests** - All integration tests (fast first, then all)

**Frontend Jobs** (parallel):
1. **Lint** - ESLint on all JavaScript code
2. **Unit Tests** - All Jest tests
3. **Component Tests** - Component-specific tests
4. **Integration Tests** - Integration test suite

**Coverage Jobs** (after tests):
- Coverage summary updates PR description (for PRs only)

**Summary Job**:
- Validates all jobs succeeded

### Code Quality Workflow (`code-quality.yml`)

Runs weekly and on-demand:
- Security scans (backend: safety, bandit; frontend: npm audit)
- Code quality metrics (backend: pylint, radon; frontend: ESLint)

## Coverage Strategy

### Coverage is for Insight, Not Gating

We collect coverage data on pull requests but **don't fail builds on coverage thresholds**.

**Why?**
- Coverage is a metric, not a goal
- 100% coverage doesn't guarantee quality
- Tests should be meaningful, not just coverage boosters

### Coverage Reporting

- **Backend**: pytest-cov generates XML, HTML, and JSON reports
- **Frontend**: Jest generates lcov and JSON summary reports
- **CI**: Coverage percentages are added to PR descriptions
- **Codecov**: Reports are uploaded for trend analysis (continue-on-error: true)

## Testing Best Practices

### Write Tests That Matter

✅ **Good Tests**:
- Test behavior, not implementation
- Cover edge cases and error conditions
- Are readable and maintainable
- Run quickly (unit tests < 1s each)
- Are independent and can run in any order

❌ **Avoid**:
- Tests that just call code to boost coverage
- Tests that duplicate other tests
- Tests that are flaky or timing-dependent
- Tests that require manual setup or cleanup

### Test Naming Conventions

**Backend (pytest)**:
```python
def test_analyzer_detects_angry_tone():
    """Test that analyzer correctly identifies angry tone."""
    # Arrange, Act, Assert
```

**Frontend (Jest)**:
```javascript
describe('WebSocketService', () => {
  it('should reconnect after connection loss', () => {
    // Arrange, Act, Assert
  });
});
```

## Performance Considerations

### Current Test Times

Approximate execution times:

- Backend unit tests: ~30 seconds
- Backend integration tests (fast): ~1 minute
- Backend integration tests (all): ~3 minutes
- Frontend unit tests: ~45 seconds
- Frontend component tests: ~30 seconds
- Frontend integration tests: ~1 minute

**Total CI time**: ~5-7 minutes (jobs run in parallel)

### Future Optimizations

If test times become problematic, we can:

1. **Optimize Test Code**: Make slow tests faster
2. **Better Parallelization**: Use pytest-xdist for backend, Jest's --maxWorkers for frontend
3. **Caching**: More aggressive dependency caching
4. **Hardware**: Larger GitHub Actions runners

**We will NOT**:
- Switch to selective testing
- Skip tests based on changed files
- Reduce test coverage to save time

## Maintenance

### Adding New Tests

1. **Write the test** in the appropriate directory
2. **Mark it appropriately** (backend: use pytest markers)
3. **Verify it runs locally**: `make test` (backend) or `npm test` (frontend)
4. **Push**: CI will automatically run it

No CI workflow changes needed - new tests are automatically discovered and run.

### Removing Tests

1. **Delete the test file** or specific test function
2. **Verify locally**: `make test` or `npm test`
3. **Push**: CI will automatically skip the deleted test

### Modifying Test Actions

If you need to change how tests run (e.g., add pytest flags, change Jest config):

1. **Backend**: Update `.github/actions/run-backend-tests/action.yml`
2. **Frontend**: Update `.github/actions/run-frontend-tests/action.yml`
3. **Local**: Update `pytest.ini` (backend) or `jest.config.js` (frontend)

**Important**: Always maintain full regression testing. Don't add selective test logic.

## Common Questions

### Q: Why not use selective testing to save time?

**A**: Reliability > Speed. Our tests run in ~5-7 minutes, which is acceptable. Selective testing adds complexity and can miss bugs when changes have unexpected side effects.

### Q: What if tests take 30+ minutes in the future?

**A**: We'll optimize the tests themselves or use better parallelization. Selective testing is a last resort, not a first choice.

### Q: Can I run selective tests locally?

**A**: Yes! Use pytest markers (`pytest -m unit`) or Jest patterns (`npm test -- --testPathPattern=components`) for fast local feedback. But always run the full suite before pushing.

### Q: Why separate component and integration test jobs for frontend?

**A**: Better visibility in CI. You can see at a glance which category of tests failed without digging through logs.

### Q: Should we increase coverage requirements?

**A**: No. Coverage is tracked for insight, not as a goal. Focus on writing meaningful tests, not achieving coverage percentages.

## References

- [Testing Best Practices (pytest)](https://docs.pytest.org/en/stable/goodpractices.html)
- [Jest Best Practices](https://jestjs.io/docs/testing-best-practices)
- [Martin Fowler - Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Google Testing Blog](https://testing.googleblog.com/)

---

**Last Updated**: January 2025

**Maintainers**: If you're considering adding selective testing or path filters to the CI workflow, please read this document carefully and discuss with the team first. The current approach is intentional and provides valuable reliability guarantees.
