#!/bin/bash
# Development startup script for Word Search Generator

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment"
fi

# Run the application with hot-reload enabled
echo "Starting Word Search Generator in development mode..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
