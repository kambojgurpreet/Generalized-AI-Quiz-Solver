#!/bin/bash

echo "Starting AI Quiz Solver Backend..."
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