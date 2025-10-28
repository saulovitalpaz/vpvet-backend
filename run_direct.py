"""Direct run script to bypass virtual environment issues"""
import sys
import os

# Explicitly add venv site-packages to Python path
venv_site_packages = os.path.join(os.path.dirname(__file__), '.venv', 'Lib', 'site-packages')
if venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)
    print(f"Added venv site-packages: {venv_site_packages}")

# Also add the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    print(f"Added current directory: {current_dir}")

# Add app directory to path
app_dir = os.path.join(current_dir, 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
    print(f"Added app directory: {app_dir}")

print("\nPython path updated!")
print("\nRunning VPVET Backend...")
print("-" * 50)

# Now try to run the app
if __name__ == '__main__':
    try:
        # Import app after path setup
        from app import create_app

        app = create_app()

        # Import db and create tables
        from extensions import db
        with app.app_context():
            db.create_all()
            print("Database tables created!")

        print("\nServer starting at http://localhost:5000")
        print("Admin panel: http://localhost:5000/admin")
        print("-" * 50)

        app.run(debug=True, host='0.0.0.0', port=5000)

    except ImportError as e:
        print(f"\nImportError: {e}")
        print("\nPlease make sure all dependencies are installed:")
        print("- Flask")
        print("- Flask-SQLAlchemy")
        print("- Flask-JWT-Extended")
        print("- psycopg2-binary")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()