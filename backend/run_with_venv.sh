#!/bin/bash
# Script to run the Teams Meeting Coach with virtual environment

# Activate virtual environment
source venv/bin/activate

# Run the application with provided arguments
python main.py "$@"