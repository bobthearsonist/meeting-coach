#!/bin/bash
# Script to run tests with virtual environment

# Activate virtual environment
source venv/bin/activate

# Run pytest with provided arguments
python -m pytest "$@"
