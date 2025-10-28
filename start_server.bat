@echo off
echo ======================================
echo VPVET Backend Server
echo ======================================
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Installing required packages if needed...
pip install -q flask flask-sqlalchemy flask-jwt-extended flask-cors psycopg2-binary flask-migrate

echo.
echo Starting server...
echo Server will be available at: http://localhost:5000
echo Admin panel: http://localhost:5000/admin
echo.
echo Press CTRL+C to stop
echo.

python -m app