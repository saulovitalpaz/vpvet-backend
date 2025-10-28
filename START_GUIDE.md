# How to Run the VPVET Backend

## The Issue
When running `python app.py` directly, Python can't find the modules in the `app/api` subdirectory.

## Solution

### Option 1: Use Python module mode (Recommended)
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run as module from the root directory
python -m app
```

### Option 2: Use the start script
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the start script
python start_server.py
```

### Option 3: Set PYTHONPATH
```bash
# Activate virtual environment
.venv\Scripts\activate

# Set PYTHONPATH and run
set PYTHONPATH=%PYTHONPATH%;.
python app.py
```

## Why this happens
- Python needs to know where to find the modules
- When you run `python app.py`, the current directory isn't in the Python path
- Using `python -m app` tells Python to treat `app` as a module, which fixes the import paths

## Admin Panel
Once the server is running, the admin panel is accessible at:
- Dashboard: http://localhost:5000/admin
- Clinics: http://localhost:5000/admin/clinics
- Users: http://localhost:5000/admin/users
- Clients: http://localhost:5000/admin/clients
- Uploads: http://localhost:5000/admin/uploads
- Analytics: http://localhost:5000/admin/analytics

## Test Credentials
- Email: dr.saulo@example.com
- Password: password123
(This user should have `is_dr_saulo: true` in the database)