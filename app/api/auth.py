"""Authentication endpoints"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Simple login endpoint for testing"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    # For testing: accept any email/password
    # In production, this should validate against database
    email = data.get('email', '').lower()

    # Check if this is Dr. Saulo's account
    is_dr_saulo = email in ['dr.saulo', 'admin', 'root', 'saulo@vpvet.com', 'saulo.vital@vpvet.com']

    # Set appropriate name based on email
    if is_dr_saulo:
        name = 'Dr. Saulo Vital'
        role = 'admin'
    else:
        name = email.split('@')[0].replace('.', ' ').title()  # Convert email to readable name
        role = 'secretary'

    user_data = {
        'id': 'test-id',
        'email': data.get('email'),
        'name': name,
        'role': role,
        'is_dr_saulo': is_dr_saulo
    }

    access_token = create_access_token(identity=user_data)

    return jsonify({
        'token': access_token,
        'user': user_data
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user"""
    current_user = get_jwt_identity()
    return jsonify(current_user)