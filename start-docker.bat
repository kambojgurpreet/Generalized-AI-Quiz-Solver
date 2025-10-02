@echo off
echo.
echo ==========================================
echo   AI Quiz Solver - Docker Setup
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Docker is not installed or not running!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Docker Compose is not available!
    echo Please ensure Docker Compose is installed.
    echo.
    pause
    exit /b 1
)

echo Docker is available ✓
echo.

REM Check if .env file exists
if not exist "backend\.env" (
    echo Creating .env file from template...
    copy "backend\.env.example" "backend\.env"
    echo.
    echo IMPORTANT: Please edit backend\.env file and add your OpenAI API key!
    echo.
    echo Opening .env file in notepad...
    notepad "backend\.env"
    echo.
    echo Press any key once you've added your OpenAI API key...
    pause >nul
)

echo Starting AI Quiz Solver with Docker...
echo.
echo Services starting:
echo - Redis Database (port 6379)
echo - FastAPI Backend (port 8000)
echo.

REM Start services
docker-compose -f docker-compose.dev.yml up --build

echo.
echo Services stopped.
pause