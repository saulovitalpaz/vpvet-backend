#!/usr/bin/env python3
"""
VPVET Admin Panel Startup Script

This script starts the Flask backend server for the VPVET admin panel.
The server will run on http://localhost:5000 with CORS enabled for the frontend.

Usage:
    python start_admin.py

Or using virtual environment:
    .venv/Scripts/python.exe start_admin.py

Features:
- Creates database tables if they don't exist
- Runs in debug mode for development
- CORS enabled for frontend at http://localhost:3001
- Admin panel endpoints available at /api/admin/*
"""

import os
import sys

def main():
    """Main function to start the admin panel server"""
    print("Starting VPVET Admin Panel...")
    print("Frontend URL: http://localhost:3001")
    print("Backend API: http://localhost:5000/api")
    print("Admin Panel: http://localhost:5000/api/admin/*")
    print()

    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    # Set environment for development
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'

    try:
        # Import the app factory and extensions
        from app import create_app
        from extensions import db

        print("Successfully imported application modules")

        # Create the Flask app
        app = create_app()
        print("Flask application created successfully")

        # Test database connection and create tables
        with app.app_context():
            try:
                # Test database connection
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                print("Database connection successful")

                # Create all tables
                db.create_all()
                print("Database tables created/verified")

            except Exception as e:
                print(f"Database connection issue: {e}")
                print("   Server will start but database features may not work")

        print()
        print("Admin Panel Features Available:")
        print("   - Create client accounts")
        print("   - Create and manage clinics")
        print("   - Create secretaries and link to clinics")
        print("   - Upload exam notes (PDF)")
        print("   - Upload radiography pictures")
        print()
        print("API Endpoints:")
        print("   GET  /api/health              - Server health check")
        print("   POST /api/auth/login          - Admin login")
        print("   GET  /api/admin/clinics       - List clinics")
        print("   POST /api/admin/clinics       - Create clinic")
        print("   GET  /api/admin/users         - List users")
        print("   POST /api/admin/users         - Create user/secretary")
        print("   GET  /api/admin/clients       - List clients")
        print("   POST /api/admin/uploads       - Upload files")
        print("   GET  /api/admin/analytics/dashboard - Dashboard stats")
        print()
        print("Note: Admin access requires Dr. Saulo credentials")
        print()
        print("Press CTRL+C to stop the server")
        print("=" * 60)

        # Start the Flask development server
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )

    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nTroubleshooting:")
        print("   1. Make sure you're in the project root directory")
        print("   2. Activate virtual environment:")
        print("      .venv\\Scripts\\activate")
        print("   3. Install dependencies:")
        print("      pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"Failed to start server: {e}")
        print("\nTroubleshooting:")
        print("   1. Check database connection in .env file")
        print("   2. Make sure PostgreSQL is running")
        print("   3. Verify all dependencies are installed")
        sys.exit(1)

if __name__ == '__main__':
    main()