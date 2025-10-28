@echo off
echo ====================================
echo VPVET Backend - Admin Panel
echo ====================================
echo.

REM Set PYTHONPATH to include virtual environment packages
set PYTHONPATH=C:\Users\user\Documents\vpet-backend\.venv\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;C:\Users\user\Documents\vpet-backend

REM Check if admin module exists
if not exist "app\api\admin\__init__.py" (
    echo ERROR: admin module not found!
    echo Please ensure all files are in place.
    pause
    exit /b 1
)

echo.
echo Starting VPVET Backend Server...
echo.
echo Server will be available at: http://localhost:5000
echo Admin Panel: http://localhost:5000/admin
echo.
echo Press CTRL+C to stop
echo.

REM Use the virtual environment Python directly
C:\Users\user\Documents\vpet-backend\.venv\Scripts\python.exe -m app