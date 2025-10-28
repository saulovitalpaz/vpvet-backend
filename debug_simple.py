"""Simple debug without unicode issues"""
import os
import sys

print("=== Debug Info ===")
print(f"Current directory: {os.getcwd()}")
print(f"app/api directory exists: {os.path.exists('app/api')}")
print(f"app/api/admin init exists: {os.path.exists('app/api/admin/__init__.py')}")

# Check app/api directory
api_dir = 'app/api'
if os.path.exists(api_dir):
    print("Contents of app/api:")
    for item in os.listdir(api_dir):
        print(f"  - {item}")
        if item == 'admin':
            admin_init = os.path.join(api_dir, 'admin', '__init__.py')
            if os.path.exists(admin_init):
                print(f"    admin/__init__.py exists")
            else:
                print(f"    admin/__init__.py MISSING!")

# Try imports
try:
    from app.api.admin import admin_bp
    print("SUCCESS: admin_bp imported")
except Exception as e:
    print(f"FAILED to import admin_bp: {e}")
    print("Type:", type(e).__name__)

input("\nPress Enter to exit...")