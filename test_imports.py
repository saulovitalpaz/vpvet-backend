"""Test all imports for the admin module"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Python path:", sys.path[:3])
print("Current directory:", os.getcwd())
print("\nTesting imports...")

try:
    from flask import Flask
    print("✓ Flask imported")
except ImportError as e:
    print(f"✗ Flask import failed: {e}")

try:
    from models.user import User
    print("✓ User model imported")
except ImportError as e:
    print(f"✗ User model import failed: {e}")

try:
    from api.admin import admin_bp
    print("✓ Admin blueprint imported")
except ImportError as e:
    print(f"✗ Admin blueprint import failed: {e}")

# Check if app directory is in path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
if app_dir in sys.path:
    print("\n✓ app directory is in Python path")
else:
    print("\n✗ app directory is NOT in Python path")
    sys.path.append(app_dir)
    print("Added app directory to Python path")

# Try importing app after path fix
try:
    import app
    print("✓ App module imported successfully")
except ImportError as e:
    print(f"✗ App module import failed: {e}")