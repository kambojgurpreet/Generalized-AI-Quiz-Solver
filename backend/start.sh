#!/bin/bash

echo "Starting AI Quiz Solver Backend..."
echo

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Create virtual environment..."
    # python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

# Start the FastAPI server
echo "Starting FastAPI server..."
echo "Server will be available at: http://localhost:8000"
echo "API docs will be available at: http://localhost:8000/docs"
echo

python main.py