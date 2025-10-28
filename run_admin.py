"""Admin Panel Test Runner"""
import sys
import os
import subprocess

# Set up paths
current_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(current_dir, '.venv', 'Scripts', 'python.exe')

# Run backend using virtual environment Python
cmd = [
    venv_python,
    '-m', 'app'
]

print("Starting VPVET Backend with Admin Panel...")
print("=" * 50)
print(f"Python: {venv_python}")
print(f"Directory: {current_dir}")
print("=" * 50)
print("\nAdmin Panel Features:")
print("- Clinic Management")
print("- User Management")
print("- Client Management")
print("- Medical Uploads")
print("- Analytics Dashboard")
print("\nServer will be available at:")
print("- API: http://localhost:5000/api")
print("- Admin: http://localhost:5000/admin")
print("=" * 50)

# Run the server
try:
    subprocess.run(cmd, check=True)
except KeyboardInterrupt:
    print("\nServer stopped.")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()