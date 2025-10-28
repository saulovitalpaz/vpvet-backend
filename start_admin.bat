@echo off
REM VPVET Admin Panel Startup Script for Windows

echo ========================================
echo   VPVET Admin Panel Startup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo.
    echo 🔧 To create virtual environment:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Found virtual environment
echo 🚀 Starting admin panel server...
echo.

REM Activate virtual environment and start server
call .venv\Scripts\activate.bat
python start_admin.py

echo.
echo Server stopped.
pause