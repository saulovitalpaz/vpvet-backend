from flask import request, jsonify
from models.user import User
from models.user import Clinic
from extensions import db
from werkzeug.security import generate_password_hash
import secrets
from . import admin_bp, admin_required

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users across all clinics"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        role = request.args.get('role', '')
        clinic_id = request.args.get('clinic_id', '')
        is_active = request.args.get('is_active', type=bool)

        # Build query
        query = User.query

        # Apply filters
        if search:
            query = query.filter(
                User.name.ilike(f'%{search}%') |
                User.email.ilike(f'%{search}%')
            )

        if role:
            query = query.filter(User.role == role)

        if clinic_id:
            query = query.filter(User.clinic_id == clinic_id)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Order by created date
        query = query.order_by(User.created_at.desc())

        # Paginate
        users = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        users_data = []
        for user in users.items:
            user_data = {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'is_dr_saulo': user.is_dr_saulo,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }

            # Add clinic info if not Dr. Saulo
            if user.clinic:
                user_data['clinic'] = {
                    'id': str(user.clinic.id),
                    'name': user.clinic.name,
                    'email': user.clinic.email
                }

            users_data.append(user_data)

        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200

    except Exception as e:
        return {'error': 'Failed to fetch users', 'details': str(e)}, 500

@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """Create a new user (secretary)"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'email', 'password', 'clinic_id']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400

        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return {'error': 'A user with this email already exists'}, 400

        # Verify clinic exists
        clinic = Clinic.query.get(data['clinic_id'])
        if not clinic:
            return {'error': 'Clinic not found'}, 404

        # Generate password hash
        password_hash = generate_password_hash(data['password'])

        # Create new user (secretary by default)
        user = User(
            clinic_id=data['clinic_id'],
            name=data['name'],
            email=data['email'],
            password_hash=password_hash,
            role=data.get('role', 'secretary'),
            is_active=data.get('is_active', True)
        )

        db.session.add(user)
        db.session.commit()

        return {
            'message': 'User created successfully',
            'user': {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'clinic': {
                    'id': str(clinic.id),
                    'name': clinic.name
                }
            }
        }, 201

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to create user', 'details': str(e)}, 500

@admin_bp.route('/users/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update an existing user"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        # Prevent updating Dr. Saulo's role
        if user.is_dr_saulo:
            return {'error': 'Cannot modify system owner account'}, 403

        # Update fields
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            # Check if email already exists for another user
            existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
            if existing:
                return {'error': 'Another user with this email already exists'}, 400
            user.email = data['email']
        if 'clinic_id' in data:
            # Verify clinic exists
            clinic = Clinic.query.get(data['clinic_id'])
            if not clinic:
                return {'error': 'Clinic not found'}, 404
            user.clinic_id = data['clinic_id']
        if 'role' in data:
            # Prevent changing role to dr_saulo
            if data['role'] == 'dr_saulo':
                return {'error': 'Cannot assign system owner role'}, 400
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])

        db.session.commit()

        user_data = {
            'id': str(user.id),
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }

        if user.clinic:
            user_data['clinic'] = {
                'id': str(user.clinic.id),
                'name': user.clinic.name
            }

        return {
            'message': 'User updated successfully',
            'user': user_data
        }, 200

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to update user', 'details': str(e)}, 500

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user (soft delete by deactivating)"""
    try:
        user = User.query.get_or_404(user_id)

        # Prevent deleting Dr. Saulo
        if user.is_dr_saulo:
            return {'error': 'Cannot delete system owner account'}, 403

        # Soft delete
        user.is_active = False
        db.session.commit()

        return {'message': 'User deactivated successfully'}, 200

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to delete user', 'details': str(e)}, 500

@admin_bp.route('/users/<user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """Reset user password to a new random password"""
    try:
        user = User.query.get_or_404(user_id)

        # Prevent resetting Dr. Saulo's password
        if user.is_dr_saulo:
            return {'error': 'Cannot reset system owner password'}, 403

        # Generate random password
        new_password = secrets.token_urlsafe(12)
        user.password_hash = generate_password_hash(new_password)

        db.session.commit()

        return {
            'message': 'Password reset successfully',
            'new_password': new_password  # In production, this should be sent via email
        }, 200

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to reset password', 'details': str(e)}, 500