@echo off
echo ====================================
echo VPVET Backend Server - Fixed
echo ====================================
echo.

REM Use the virtual environment's Python directly
echo Using virtual environment Python...
set PYTHON_PATH=C:\Users\user\Documents\vpet-backend\.venv\Lib\site-packages
set PATH=C:\Users\user\Documents\vpet-backend\.venv\Scripts;%PATH%

echo.
echo Python path: %PYTHON_PATH%
echo.
echo Installing missing packages...
C:\Users\user\Documents\vpet-backend\.venv\Scripts\pip.exe install -q psycopg2-binary

echo.
echo Starting server...
echo.
echo Server: http://localhost:5000
echo Admin: http://localhost:5000/admin
echo.
C:\Users\user\Documents\vpet-backend\.venv\Scripts\python.exe -m app