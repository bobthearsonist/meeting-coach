#!/bin/bash
# Regression Testing Validation Script
# =====================================
# This script validates that the project maintains its regression testing approach.
# It checks for selective testing tools and configurations that should NOT be present.
#
# Run this script in CI or locally before committing changes to test configuration.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔍 Validating Regression Testing Configuration..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Function to report an error
error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
    ERRORS=$((ERRORS + 1))
}

# Function to report a warning
warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
}

# Function to report success
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Check 1: Backend - No selective testing tools
echo "Checking backend dependencies..."
if [ -f "$PROJECT_ROOT/backend/requirements.txt" ]; then
    if grep -qi "pytest-testmon\|pytest-picked\|pytest-incremental" "$PROJECT_ROOT/backend/requirements.txt"; then
        error "Backend requirements.txt contains selective testing tools (pytest-testmon, pytest-picked, etc.)"
    else
        success "No selective testing tools in backend dependencies"
    fi
else
    warning "Backend requirements.txt not found"
fi

# Check 2: Frontend - No selective testing configuration
echo "Checking frontend package.json..."
if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    if grep -qi '"onlyChanged"\|"changedSince"\|"changedFilesWithAncestor"' "$PROJECT_ROOT/frontend/package.json"; then
        error "Frontend package.json contains selective testing configuration (onlyChanged, changedSince, etc.)"
    else
        success "No selective testing configuration in frontend package.json"
    fi
else
    warning "Frontend package.json not found"
fi

# Check 3: Frontend jest.config.js - No selective testing
if [ -f "$PROJECT_ROOT/frontend/jest.config.js" ]; then
    # Look for actual usage, not comments about what not to do
    if grep -v "^[[:space:]]*//\|^[[:space:]]*\*" "$PROJECT_ROOT/frontend/jest.config.js" | grep -qi "onlyChanged\|changedSince\|changedFilesWithAncestor"; then
        error "Frontend jest.config.js contains selective testing configuration"
    else
        success "No selective testing in jest.config.js"
    fi
fi

# Check 4: CI workflows - No path filters on test jobs
echo "Checking CI workflows..."
if [ -f "$PROJECT_ROOT/.github/workflows/ci.yml" ]; then
    # Check if any test jobs have path filters (they shouldn't)
    # Look for specific test job names we know about
    if grep -A 30 "^\s*backend-unit-tests:\|^\s*backend-integration-tests:\|^\s*frontend-unit-tests:\|^\s*frontend-component-tests:\|^\s*frontend-integration-tests:" "$PROJECT_ROOT/.github/workflows/ci.yml" | grep -q "^\s*paths:"; then
        error "CI workflow contains path filters on test jobs"
    else
        success "No path filters on test jobs in CI workflow"
    fi
else
    warning "CI workflow file not found"
fi

# Check 5: Test scripts don't use selective flags
echo "Checking test scripts..."
if [ -f "$PROJECT_ROOT/Makefile" ]; then
    if grep -E "pytest.*--testmon|jest.*--onlyChanged" "$PROJECT_ROOT/Makefile"; then
        error "Makefile contains selective testing flags"
    else
        success "No selective testing flags in Makefile"
    fi
fi

# Check 6: Documentation exists
echo "Checking documentation..."
if [ -f "$PROJECT_ROOT/TESTING_STRATEGY.md" ]; then
    success "TESTING_STRATEGY.md exists"
else
    warning "TESTING_STRATEGY.md not found - please document testing approach"
fi

# Summary
echo ""
echo "========================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All validation checks passed!${NC}"
    echo "The regression testing configuration is intact."
    exit 0
else
    echo -e "${RED}❌ Found $ERRORS error(s)${NC}"
    echo ""
    echo "The regression testing configuration has been compromised."
    echo "Please review the errors above and remove any selective testing tools or configurations."
    echo ""
    echo "See TESTING_STRATEGY.md for details on our testing philosophy."
    exit 1
fi
