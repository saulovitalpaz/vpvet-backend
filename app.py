from flask import Flask, jsonify
from flask_cors import CORS
from datetime import timedelta
import os

from extensions import db, jwt, migrate

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg://postgres:postgres@localhost/vpvet'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    # Allow all origins for local testing
    CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}}, supports_credentials=True)

    # Import models so Flask-Migrate can detect them
    from models.user import Clinic, User
    from models.patient import Tutor, Animal
    from models.appointment import Appointment
    from models.exam import Consultation, ExamResult

    # Register blueprints (we'll create these next)
    from api.auth import auth_bp
    from api.appointments import appointments_bp
    from api.patients import patients_bp
    from api.consultations import consultations_bp
    from api.public import public_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(consultations_bp)
    app.register_blueprint(public_bp)

    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy'}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
