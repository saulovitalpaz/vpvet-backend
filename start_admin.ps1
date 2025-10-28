# VPVET Backend Admin Panel - PowerShell Startup Script

Write-Host "====================================" -ForegroundColor Green
Write-Host "VPVET Backend - Admin Panel" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Set up virtual environment
$venvPath = "C:\Users\user\Documents\vpet-backend\.venv"
$projectPath = "C:\Users\user\Documents\vpet-backend"

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& $venvPath\Scripts\Activate.ps1

# Check if activation was successful
if ($env:VIRTUAL_ENV) {
    Write-Host "Virtual environment activated successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Please check the virtual environment path" -ForegroundColor Red
    exit 1
}

# Set Python path to include venv packages
$env:PYTHONPATH = "$venvPath\Lib\site-packages;$env:PYTHONPATH"
$env:PYTHONPATH = "$projectPath;$env:PYTHONPATH"

Write-Host ""
Write-Host "Starting VPVET Backend Server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Admin Panel: http://localhost:5000/admin" -ForegroundColor Yellow
Write-Host ""

# Start the application
Write-Host "Press CTRL+C to stop" -ForegroundColor White

try {
    # Use python from venv
    & python -m app
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}