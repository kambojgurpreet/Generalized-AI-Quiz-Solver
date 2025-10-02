#!/bin/bash

echo
echo "=========================================="
echo "  AI Quiz Solver - Docker Setup"
echo "=========================================="
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed!"
    echo "Please install Docker from: https://www.docker.com/get-started"
    echo
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not available!"
    echo "Please ensure Docker Compose is installed."
    echo
    exit 1
fi

echo "Docker is available ✓"
echo

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "Creating .env file from template..."
    cp "backend/.env.example" "backend/.env"
    echo
    echo "IMPORTANT: Please edit backend/.env file and add your OpenAI API key!"
    echo
    read -p "Press Enter once you've added your OpenAI API key..."
fi

echo "Starting AI Quiz Solver with Docker..."
echo
echo "Services starting:"
echo "- Redis Database (port 6379)"
echo "- FastAPI Backend (port 8000)"
echo

# Start services
docker-compose -f docker-compose.dev.yml up --build

echo
echo "Services stopped."