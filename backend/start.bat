@echo off
echo Starting AI Quiz Solver Backend...
echo.

REM Check if Redis is running
echo Checking Redis connection...
redis-cli ping > nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Redis server is not running!
    echo Running without Redis - caching will be disabled.
    echo.
    echo To enable caching, you can:
    echo 1. Install Redis from: https://redis.io/download
    echo 2. Use Docker: docker run -d -p 6379:6379 redis:alpine
    echo 3. Use the Docker setup: ..\start-docker.bat
    echo.
    echo Continuing without Redis in 3 seconds...
    timeout /t 3 /nobreak > nul
) else (
    echo Redis is running ✓
)
echo.

REM Set environment variables
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and add your OpenAI API key!
    echo.
    pause
)

REM Start the FastAPI server
echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API docs will be available at: http://localhost:8000/docs
echo.

"D:/Web/Generalized AI Quiz Solver/.venv/Scripts/python.exe" main.py