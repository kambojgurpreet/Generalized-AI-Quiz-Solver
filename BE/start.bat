@echo off
echo Starting AI Quiz Solver Backend...
echo.

echo "Activating virtual environment..."
call .venv/Scripts/activate.bat

echo "Installing dependencies..."
pip install -r requirements.txt

REM Start the FastAPI server
echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API docs will be available at: http://localhost:8000/docs
echo.

python main.py