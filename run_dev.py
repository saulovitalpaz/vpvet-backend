"""Run the VPVET Flask app in development mode"""
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set Flask environment variables
os.environ['FLASK_APP'] = 'app'
os.environ['FLASK_ENV'] = 'development'

# Import and run the app
from app import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Import db after app context
        from extensions import db
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)