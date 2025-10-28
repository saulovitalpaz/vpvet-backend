"""Run the VPVET Flask app"""
import os
import sys

# Add the root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set FLASK_APP
os.environ['FLASK_APP'] = 'app'

# Import and run the app
from app import create_app
from extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)