#!/bin/bash

echo "Starting AI Quiz Solver Backend..."
echo

# Check if Redis is running
echo "Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "WARNING: Redis server is not running!"
    echo "Please start Redis server before running the backend."
    echo
    echo "You can start Redis with:"
    echo "  - On macOS: brew services start redis"
    echo "  - On Ubuntu: sudo systemctl start redis"
    echo "  - Using Docker: docker run -d -p 6379:6379 redis:alpine"
    echo
    exit 1
fi

echo "Redis is running ✓"
echo

# Set environment variables
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo
    echo "IMPORTANT: Please edit .env file and add your OpenAI API key!"
    echo
    read -p "Press any key to continue..."
fi

# Start the FastAPI server
echo "Starting FastAPI server..."
echo "Server will be available at: http://localhost:8000"
echo "API docs will be available at: http://localhost:8000/docs"
echo

python main.py