@echo off
echo Starting AI Quiz Solver Backend...
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