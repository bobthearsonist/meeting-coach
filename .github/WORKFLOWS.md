# GitHub Actions Workflows Documentation

This document describes the automated testing and CI/CD workflows for the Meeting Coach project.

## Overview

The project uses GitHub Actions to automate testing, code quality checks, and build verification. All workflows are designed to:

- Run in parallel where possible for fast feedback
- Provide clear, actionable error messages
- Generate artifacts for debugging
- Support both push and pull request events
- Use dependency caching for faster runs

## Workflows

### 1. CI Workflow (`ci.yml`)

**Purpose**: Main integration workflow that runs all critical tests

**Triggers**: 
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual workflow dispatch

**Jobs**:
- `backend-lint`: Lint Python code (black, isort, pylint, flake8)
- `backend-unit-tests`: Run backend unit tests
- `backend-integration-tests`: Run backend integration tests
- `frontend-lint`: Lint JavaScript/React code (ESLint)
- `frontend-unit-tests`: Run frontend unit tests with coverage
- `frontend-integration-tests`: Run frontend integration tests
- `ci-success`: Summary job that verifies all tests passed

**Success Criteria**: All lint and test jobs must pass

**Typical Duration**: 5-8 minutes

---

### 2. Backend Tests Workflow (`backend-tests.yml`)

**Purpose**: Comprehensive backend testing with detailed test separation

**Triggers**:
- Push to `main` or `develop` with backend changes
- Pull requests to `main` or `develop` with backend changes
- Manual workflow dispatch

**Jobs**:

#### `setup`
- Installs Python dependencies
- Runs code formatting checks (black, isort)
- Runs linting (pylint, flake8)

#### `unit-tests`
- Runs unit tests with pytest
- Tests marked with `@pytest.mark.unit`
- Generates coverage reports (term, XML, HTML)
- Uploads coverage to Codecov
- **Matrix Strategy**: Python 3.12

#### `integration-tests`
- Runs integration tests
- Excludes slow tests and tests requiring external dependencies
- Tests marked with `@pytest.mark.integration`

#### `system-tests`
- Runs only on `main` branch or manual dispatch
- Tests full pipeline with mocked dependencies
- Continues on failure (non-blocking)

**Test Markers Used**:
- `unit`: Unit tests (fast, isolated)
- `integration`: Integration tests
- `slow`: Slow-running tests
- `requires_ollama`: Tests needing Ollama LLM
- `requires_audio`: Tests needing audio hardware

**Success Criteria**: Setup, unit tests, and integration tests must pass

**Typical Duration**: 6-10 minutes

---

### 3. Frontend Tests Workflow (`frontend-tests.yml`)

**Purpose**: Comprehensive frontend testing with component and integration tests

**Triggers**:
- Push to `main` or `develop` with frontend changes
- Pull requests to `main` or `develop` with frontend changes
- Manual workflow dispatch

**Jobs**:

#### `setup`
- Installs Node.js dependencies
- Runs ESLint
- Checks code formatting with Prettier

#### `unit-tests`
- Runs unit tests with Jest
- Excludes integration and e2e tests
- Generates coverage reports
- Uploads coverage to Codecov
- **Matrix Strategy**: Node.js 18, 20

#### `component-tests`
- Runs component-specific tests
- Tests in `components/` directory
- Tests in `screens/` directory

#### `integration-tests`
- Tests WebSocket service integration
- Tests Context API and state management
- Tests with `.integration.test.js` suffix

#### `build-test`
- Runs only on `main` branch pushes
- Verifies macOS build succeeds
- Installs CocoaPods dependencies
- Runs on macOS runner

**Success Criteria**: Setup, unit tests, component tests, and integration tests must pass

**Typical Duration**: 8-12 minutes

---

### 4. Pull Request Checks Workflow (`pr-checks.yml`)

**Purpose**: Fast validation for pull requests to provide quick feedback

**Triggers**: Pull request events (opened, synchronize, reopened, ready_for_review)

**Jobs**:

#### `changes`
- Detects which parts of the codebase changed
- Outputs: `backend`, `frontend`, `workflows`
- Uses `dorny/paths-filter` action

#### `backend-quick-check`
- Runs only if backend files changed
- Quick lint check (black, isort)
- Runs fast unit tests only
- Fails fast on first error (`-x` flag)

#### `frontend-quick-check`
- Runs only if frontend files changed
- Quick lint check (ESLint)
- Runs fast tests with `--bail` flag

#### `pr-size-check`
- Calculates changed lines
- Warns if PR > 500 lines
- Non-blocking

#### `pr-title-check`
- Validates conventional commits format
- Non-blocking (warning only)

**Success Criteria**: Quick checks for changed components must pass

**Typical Duration**: 3-5 minutes

---

### 5. Code Quality Workflow (`code-quality.yml`)

**Purpose**: Security scans and code quality metrics

**Triggers**:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Weekly schedule (Mondays at 9 AM UTC)
- Manual workflow dispatch

**Jobs**:

#### `backend-security`
- Runs `safety` to check for vulnerable dependencies
- Runs `bandit` for security linting
- Uploads security reports as artifacts

#### `frontend-security`
- Runs `npm audit` for dependency vulnerabilities
- Uploads audit reports as artifacts

#### `backend-code-quality`
- Runs pylint with detailed reporting
- Calculates code complexity with `radon`
- Generates quality metrics

#### `frontend-code-quality`
- Runs ESLint with JSON output
- Generates quality reports

#### `dependency-review`
- Reviews dependency changes in PRs
- Fails on moderate or higher severity issues
- Checks license compatibility

**All Jobs**: Continue on error (non-blocking for now)

**Typical Duration**: 4-6 minutes

---

### 6. Test Coverage Workflow (`coverage.yml`)

**Purpose**: Detailed coverage analysis and reporting

**Triggers**:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Jobs**:

#### `backend-coverage`
- Runs all fast backend tests with coverage
- Generates coverage badge data
- Uploads to Codecov
- Comments coverage percentage on PRs
- Uploads HTML report as artifact

#### `frontend-coverage`
- Runs all frontend tests with coverage
- Generates coverage badge data
- Uploads to Codecov
- Comments coverage percentage on PRs
- Uploads HTML report as artifact

**Coverage Formats Generated**:
- Terminal output (for logs)
- XML (for Codecov)
- HTML (for detailed viewing)
- JSON (for programmatic access)

**Typical Duration**: 5-7 minutes

---

## Workflow Dependencies

```
CI Workflow:
  backend-lint → backend-unit-tests → backend-integration-tests
  frontend-lint → frontend-unit-tests → frontend-integration-tests
  → ci-success

Backend Tests:
  setup → unit-tests → integration-tests → system-tests
  → test-summary

Frontend Tests:
  setup → unit-tests → component-tests → integration-tests → build-test
  → test-summary

PR Checks:
  changes → [backend-quick-check, frontend-quick-check]
  pr-size-check (independent)
  pr-title-check (independent)
  → pr-checks-summary
```

## Branch Protection Rules (Recommended)

Configure these branch protection rules for `main` and `develop`:

```yaml
Required status checks:
  - CI Success
  - Backend Quick Check (if backend changes)
  - Frontend Quick Check (if frontend changes)
  - Backend Unit Tests
  - Frontend Unit Tests

Additional settings:
  - Require branches to be up to date before merging
  - Require pull request reviews (1 approver)
  - Dismiss stale pull request approvals
  - Require review from Code Owners
  - Include administrators
```

## Caching Strategy

All workflows use GitHub Actions caching to speed up runs:

**Python**:
- Cache key: `pip` with dependency on `backend/requirements.txt`
- Caches pip packages

**Node.js**:
- Cache key: `npm` with dependency on `frontend/package-lock.json`
- Caches npm packages

**Benefits**: 30-50% faster runs after first execution

## Artifacts

Workflows generate the following artifacts:

| Artifact | Workflow | Retention | Purpose |
|----------|----------|-----------|---------|
| `backend-unit-coverage` | CI | 7 days | Unit test coverage |
| `frontend-unit-coverage` | CI | 7 days | Unit test coverage |
| `backend-unit-coverage-html` | Backend Tests | 7 days | Detailed coverage report |
| `backend-coverage-report` | Coverage | 14 days | Full coverage analysis |
| `frontend-coverage-report` | Coverage | 14 days | Full coverage analysis |
| `backend-security-reports` | Code Quality | 30 days | Security scan results |
| `frontend-security-reports` | Code Quality | 30 days | Security scan results |
| `backend-quality-reports` | Code Quality | 30 days | Code quality metrics |
| `frontend-quality-reports` | Code Quality | 30 days | Code quality metrics |

## Workflow Optimization

**Concurrency Control**: All workflows use concurrency groups to cancel in-progress runs when new commits are pushed.

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Parallel Execution**: Jobs that don't depend on each other run in parallel:
- Backend and frontend jobs run simultaneously
- Multiple test suites run in parallel
- Lint and test jobs are separated for faster feedback

**Matrix Strategies**: Some workflows test against multiple versions:
- Frontend tests: Node.js 18 and 20
- Backend tests: Python 3.12 (can be extended)

## Troubleshooting

### Workflow fails with "Unable to resolve action"

**Cause**: GitHub Actions version tag doesn't exist

**Solution**: Update action versions in workflow files

### Tests timeout

**Cause**: Long-running tests or waiting for external services

**Solution**: 
- Increase timeout in workflow
- Mock external dependencies
- Use `@pytest.mark.slow` to exclude from fast runs

### Coverage upload fails

**Cause**: Missing Codecov token or incorrect file paths

**Solution**: 
- Verify coverage files are generated
- Check Codecov configuration
- Use `continue-on-error: true` for non-critical uploads

### Caching not working

**Cause**: Cache key mismatch or cache size limits

**Solution**:
- Verify dependency files haven't moved
- Check cache size (max 10GB per repo)
- Clear cache manually if corrupted

## Best Practices

1. **Keep workflows fast**: Target < 10 minutes for full CI
2. **Fail fast**: Use `-x` flag in tests to stop on first failure during PR checks
3. **Use appropriate markers**: Mark tests with `slow`, `integration`, etc.
4. **Mock external dependencies**: Don't require Ollama, audio devices in CI
5. **Generate artifacts**: Upload logs and reports for debugging
6. **Cache aggressively**: Cache dependencies to speed up runs
7. **Run in parallel**: Don't create unnecessary dependencies between jobs
8. **Provide clear feedback**: Use meaningful job names and status checks

## Local Testing

Before pushing, run the same checks locally:

```bash
# Backend
cd backend
black --check *.py src/ tests/
isort --check-only *.py src/ tests/ --profile=black
pytest tests/unit/ -v -m "unit"

# Frontend
cd frontend
npm run lint
npm test -- --watchAll=false
```

## Monitoring

Monitor workflow health:
- Check workflow run times in Actions tab
- Review artifact sizes
- Monitor cache hit rates
- Track flaky tests
- Review security scan results weekly

---

For questions about workflows, see the [CONTRIBUTING.md](CONTRIBUTING.md) guide or open an issue.
