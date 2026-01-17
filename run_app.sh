#!/bin/bash
# Reachy Mini Ollama App Runner Script
# Note: This script assumes a virtual environment is available
# Adjust the path below to match your environment

# Default virtual environment path (adjust as needed)
VENV_PATH="../reachy_mini_env"

# Check if virtual environment exists
if [ -f "$VENV_PATH/bin/activate" ]; then
    echo "Activating virtual environment at $VENV_PATH"
    source "$VENV_PATH/bin/activate"
else
    echo "Warning: Virtual environment not found at $VENV_PATH"
    echo "Make sure Python dependencies are installed:"
    echo "  pip install requests numpy scipy"
    echo "And Reachy Mini SDK is installed"
    echo ""
    echo "Continue without virtual environment? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the app with any provided arguments
python app.py "$@"