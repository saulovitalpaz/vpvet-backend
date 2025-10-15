from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

appointments_bp = Blueprint('appointments', __name__, url_prefix='/api/appointments')

@appointments_bp.route('/availability', methods=['GET'])
@jwt_required()
def get_availability():
    from models.user import User
    from models.appointment import Appointment
    from flask_jwt_extended import get_jwt

    user_id = get_jwt_identity()
    claims = get_jwt()
    user = User.query.get(user_id)

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date required'}), 400

    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    # Generate all possible slots
    slots = []
    current = start.replace(hour=8, minute=0, second=0, microsecond=0)

    while current <= end:
        # Skip weekends
        if current.weekday() < 5:  # Monday=0, Sunday=6
            # Generate slots from 8am to 6pm
            for hour in range(8, 18):
                for minute in [0, 30]:
                    slot_time = current.replace(hour=hour, minute=minute)

                    # Check if occupied
                    appointment = Appointment.query.filter_by(
                        datetime=slot_time
                    ).filter(
                        Appointment.status != 'cancelled'
                    ).first()

                    slot_info = {
                        'datetime': slot_time.isoformat(),
                        'available': appointment is None
                    }

                    if appointment:
                        slot_info['appointment_id'] = str(appointment.id)
                        slot_info['clinic_id'] = str(appointment.clinic_id)

                    slots.append(slot_info)

        current += timedelta(days=1)

    # Filter based on user permissions
    for slot in slots:
        if not slot['available']:
            # Dr. Saulo sees all details
            if user.is_dr_saulo:
                appointment = Appointment.query.get(slot['appointment_id'])
                slot['appointment'] = appointment.to_dict(include_details=True)
            # Secretary only sees their clinic's details
            elif slot['clinic_id'] == str(user.clinic_id):
                appointment = Appointment.query.get(slot['appointment_id'])
                slot['appointment'] = appointment.to_dict(include_details=True)
            # Hide details for other clinics
            else:
                slot.pop('appointment_id', None)
                slot.pop('clinic_id', None)

    return jsonify({
        'period': {
            'start': start_date,
            'end': end_date
        },
        'slots': slots
    }), 200

@appointments_bp.route('', methods=['POST'])
@jwt_required()
def create_appointment():
    from models.appointment import Appointment
    from extensions import db
    from flask_jwt_extended import get_jwt

    user_id = get_jwt_identity()
    claims = get_jwt()
    data = request.get_json()

    # Validate required fields
    required = ['animal_id', 'datetime', 'service_type']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        appointment_time = datetime.fromisoformat(data['datetime'])
    except ValueError:
        return jsonify({'error': 'Invalid datetime format'}), 400

    # Check for conflicts with pessimistic locking
    existing = db.session.query(Appointment).with_for_update().filter_by(
        datetime=appointment_time
    ).filter(
        Appointment.status != 'cancelled'
    ).first()

    if existing:
        # Find next available slot
        current = appointment_time
        next_available = None
        for _ in range(20):
            current += timedelta(minutes=30)
            conflict = db.session.query(Appointment).filter_by(
                datetime=current
            ).filter(
                Appointment.status != 'cancelled'
            ).first()
            if not conflict:
                next_available = current
                break

        return jsonify({
            'error': 'Time slot already occupied',
            'next_available': next_available.isoformat() if next_available else None
        }), 409

    # Get clinic_id - if user doesn't have one (Dr. Saulo), we need to get it from the request or use a default
    clinic_id = claims.get('clinic_id')

    # If user doesn't have a clinic (Dr. Saulo case), require clinic_id in the request or use first available
    if not clinic_id:
        if 'clinic_id' in data:
            clinic_id = data['clinic_id']
        else:
            # For Dr. Saulo, use the first clinic as default (his own practice)
            from models.user import Clinic
            default_clinic = Clinic.query.first()
            if default_clinic:
                clinic_id = str(default_clinic.id)
            else:
                return jsonify({'error': 'No clinic available for appointment'}), 400

    # Create appointment
    appointment = Appointment(
        clinic_id=clinic_id,
        animal_id=data['animal_id'],
        datetime=appointment_time,
        duration_minutes=data.get('duration_minutes', 30),
        service_type=data['service_type'],
        notes=data.get('notes'),
        created_by=user_id
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        'appointment': appointment.to_dict(include_details=True)
    }), 201

@appointments_bp.route('/<appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    from models.user import User
    from models.appointment import Appointment

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    # Check permissions
    if not user.is_dr_saulo and str(appointment.clinic_id) != str(user.clinic_id):
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({
        'appointment': appointment.to_dict(include_details=True)
    }), 200

@appointments_bp.route('/<appointment_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    from models.user import User
    from models.appointment import Appointment
    from extensions import db

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    # Check permissions
    if not user.is_dr_saulo and str(appointment.clinic_id) != str(user.clinic_id):
        return jsonify({'error': 'Access denied'}), 403

    # Soft delete - mark as cancelled instead of actually deleting
    appointment.status = 'cancelled'
    db.session.commit()

    return jsonify({'message': 'Appointment cancelled successfully'}), 200
