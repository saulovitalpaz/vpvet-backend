"""Debug import issues"""
import os
import sys

print("\n=== Debug Import Issues ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print("\nPython path:")
for p in sys.path[:10]:
    print(f"  - {p}")

# Try to list what's in app/api
api_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'api')
print(f"\napp/api path: {api_path}")
print(f"app/api exists: {os.path.exists(api_path)}")
if os.path.exists(api_path):
    print("Contents:")
    for item in os.listdir(api_path):
        print(f"  - {item}")
        init_file = os.path.join(api_path, item, '__init__.py')
        if os.path.exists(init_file):
            print(f"    ✓ Has __init__.py")
        else:
            print(f"    ✗ Missing __init__.py")

# Try imports
print("\nTesting imports:")
try:
    from app import create_app
    print("✓ app.create_app")
except ImportError as e:
    print(f"✗ app.create_app: {e}")

try:
    from extensions import db
    print("✓ extensions.db")
except ImportError as e:
    print(f"✗ extensions.db: {e}")