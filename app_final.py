"""VPVET Backend Application - Fixed Version"""
import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import timedelta, datetime
import logging
from sqlalchemy import text

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import extensions
from extensions import db, jwt, migrate
from utils.environment import get_environment_config, validate_environment_config
from models.user import Clinic, User
from models.patient import Tutor, Animal
from models.appointment import Appointment
from models.exam import Consultation, ExamResult

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Configure logging
    if os.getenv('FLASK_ENV') == 'production':
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)

    # Configuration
    database_url = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg://postgres:postgres@localhost/vpvet'
    )
    # Railway uses postgresql:// but SQLAlchemy with psycopg needs postgresql+psycopg://
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    # Get environment configuration for CORS
    env_config = get_environment_config()

    # Validate environment configuration for safety
    if not validate_environment_config(env_config):
        app.logger.error("Invalid environment configuration detected!")
        raise RuntimeError("Environment configuration validation failed")

    app.logger.info(f"Environment: {env_config['environment']}")
    app.logger.info(f"Configuring CORS for origins: {env_config['allowed_origins']}")

    # Configure CORS with environment-aware settings
    CORS(app,
         resources={r"/api/*": {
             "origins": env_config['allowed_origins'],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "X-Environment"],
             "expose_headers": ["Content-Type", "Authorization", "X-Environment"],
             "supports_credentials": True,
             "max_age": 3600
         }})

    # Enhanced after_request handler with environment awareness
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')

        # Check if origin is in allowed origins
        if origin in env_config['allowed_origins']:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Environment')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')

            # Add environment information for debugging
            response.headers.add('X-Environment', env_config['environment'])
            response.headers.add('X-API-Version', '1.0.0')

        return response

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Import blueprints
    from api.auth import auth_bp
    from api.appointments import appointments_bp
    from api.patients import patients_bp
    from api.consultations import consultations_bp
    from api.public import public_bp
    from api.clients import clients_bp
    from app.api.admin import admin_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(consultations_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(admin_bp)

    # Add health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })

    return app

# Create app instance for Railway/Gunicorn
app = create_app()


# Run the application
if __name__ == '__main__':
    app = create_app()

    # Import db after app creation
    from extensions import db

    # Create tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

    app.logger.info("Starting VPVET Backend Server...")
    app.logger.info(f"Server: http://localhost:5000")
    app.logger.info(f"Admin Panel: http://localhost:5000/admin")

    app.run(debug=True, host='0.0.0.0', port=5000)