"""Final run script for VPVET Backend with Admin Panel"""
import os
import sys
import subprocess

def main():
    """Run VPVET Backend"""
    # Set up environment
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(current_dir, '.venv', 'Scripts', 'python.exe')

    # Check if venv python exists
    if not os.path.exists(venv_python):
        print("ERROR: Virtual environment Python not found!")
        print(f"Expected: {venv_python}")
        return 1

    # Set FLASK_APP to point to app module in current directory
    env = os.environ.copy()
    env['FLASK_APP'] = 'app_final'  # Use the fixed version

    print("=" * 50)
    print("VPVET Backend with Admin Panel")
    print("=" * 50)
    print(f"Python: {venv_python}")
    print(f"Directory: {current_dir}")
    print()
    print("Available Commands:")
    print("1. python -m app_final  # Run with admin panel")
    print("2. python app_final.py     # Run without admin panel")
    print()
    print("=" * 50)

    # Run the application
    try:
        # Using subprocess to properly handle virtual environment
        result = subprocess.run(
            [venv_python, '-m', 'app_final'],
            env=env,
            check=True
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())