@echo off
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting VPVET Backend Server...
echo.
echo Server will be available at: http://localhost:5000
echo Admin Panel: http://localhost:5000/admin
echo.
python -m app