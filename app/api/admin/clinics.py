from flask import request, jsonify
from models.user import Clinic
from models.user import User
from models.appointment import Appointment
from extensions import db
from . import admin_bp, admin_required

@admin_bp.route('/clinics', methods=['GET'])
@admin_required
def get_all_clinics():
    """Get all clinics with user counts and appointment statistics"""
    try:
        clinics = Clinic.query.all()
        clinics_data = []

        for clinic in clinics:
            # Count users for this clinic
            user_count = User.query.filter_by(clinic_id=clinic.id).count()
            active_user_count = User.query.filter_by(clinic_id=clinic.id, is_active=True).count()

            # Count appointments for this clinic
            appointment_count = Appointment.query.filter_by(clinic_id=clinic.id).count()

            clinics_data.append({
                'id': str(clinic.id),
                'name': clinic.name,
                'phone': clinic.phone,
                'email': clinic.email,
                'address': clinic.address,
                'created_at': clinic.created_at.isoformat() if clinic.created_at else None,
                'user_count': user_count,
                'active_user_count': active_user_count,
                'appointment_count': appointment_count
            })

        return jsonify(clinics_data), 200

    except Exception as e:
        return {'error': 'Failed to fetch clinics', 'details': str(e)}, 500

@admin_bp.route('/clinics', methods=['POST'])
@admin_required
def create_clinic():
    """Create a new clinic"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'phone', 'email']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400

        # Check if email already exists
        if Clinic.query.filter_by(email=data['email']).first():
            return {'error': 'A clinic with this email already exists'}, 400

        # Create new clinic
        clinic = Clinic(
            name=data['name'],
            phone=data['phone'],
            email=data['email'],
            address=data.get('address', '')
        )

        db.session.add(clinic)
        db.session.commit()

        return {
            'message': 'Clinic created successfully',
            'clinic': {
                'id': str(clinic.id),
                'name': clinic.name,
                'phone': clinic.phone,
                'email': clinic.email,
                'address': clinic.address
            }
        }, 201

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to create clinic', 'details': str(e)}, 500

@admin_bp.route('/clinics/<clinic_id>', methods=['PUT'])
@admin_required
def update_clinic(clinic_id):
    """Update an existing clinic"""
    try:
        clinic = Clinic.query.get_or_404(clinic_id)
        data = request.get_json()

        # Update fields
        if 'name' in data:
            clinic.name = data['name']
        if 'phone' in data:
            clinic.phone = data['phone']
        if 'email' in data:
            # Check if email already exists for another clinic
            existing = Clinic.query.filter(Clinic.email == data['email'], Clinic.id != clinic_id).first()
            if existing:
                return {'error': 'Another clinic with this email already exists'}, 400
            clinic.email = data['email']
        if 'address' in data:
            clinic.address = data['address']

        db.session.commit()

        return {
            'message': 'Clinic updated successfully',
            'clinic': {
                'id': str(clinic.id),
                'name': clinic.name,
                'phone': clinic.phone,
                'email': clinic.email,
                'address': clinic.address
            }
        }, 200

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to update clinic', 'details': str(e)}, 500

@admin_bp.route('/clinics/<clinic_id>', methods=['DELETE'])
@admin_required
def delete_clinic(clinic_id):
    """Delete a clinic (soft delete by deactivating all users)"""
    try:
        clinic = Clinic.query.get_or_404(clinic_id)

        # Deactivate all users associated with this clinic
        User.query.filter_by(clinic_id=clinic_id).update({'is_active': False})

        # Optionally, you could delete the clinic entirely
        # db.session.delete(clinic)

        db.session.commit()

        return {'message': 'Clinic deactivated successfully'}, 200

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to delete clinic', 'details': str(e)}, 500

@admin_bp.route('/clinics/<clinic_id>/users', methods=['GET'])
@admin_required
def get_clinic_users(clinic_id):
    """Get all users for a specific clinic"""
    try:
        clinic = Clinic.query.get_or_404(clinic_id)
        users = User.query.filter_by(clinic_id=clinic_id).all()

        users_data = []
        for user in users:
            users_data.append({
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })

        return jsonify(users_data), 200

    except Exception as e:
        return {'error': 'Failed to fetch clinic users', 'details': str(e)}, 500