@echo off
echo ========================================================
echo       HomeValue AI - Setup and Run Script (Windows)
echo ========================================================
echo.

echo [1/4] Checking for virtual environment...
if not exist "venv" (
    echo Creating new Python virtual environment...
    python -m venv venv
) else (
    echo Virtual environment found!
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Installing / Updating Python dependencies...
pip install -r requirements.txt --quiet
echo Dependencies are up to date!

echo.
echo [4/4] Starting the HomeValue AI Backend Server...
echo The app will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server.
echo.
python app\app.py

pause
