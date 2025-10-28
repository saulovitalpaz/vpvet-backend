"""Appointment endpoints"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

appointments_bp = Blueprint('appointments', __name__, url_prefix='/api/appointments')

@appointments_bp.route('/availability', methods=['GET'])
@jwt_required()
def get_availability():
    """Get appointment availability for testing"""
    # Mock data
    now = datetime.utcnow()
    available_times = []

    for i in range(7):  # Next 7 days
        date = (now + timedelta(days=i)).strftime('%Y-%m-%d')
        available_times.append({
            'date': date,
            'slots': ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00']
        })

    return jsonify({
        'availability': available_times,
        'total_slots': 8 * 7  # 8 slots per day for 7 days
    })

@appointments_bp.route('/', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get all appointments for current user"""
    current_user = get_jwt_identity()

    # Mock appointments
    appointments = [
        {
            'id': '1',
            'datetime': '2025-10-22T10:00:00',
            'duration_minutes': 60,
            'service_type': 'Consulta Rotina',
            'status': 'scheduled',
            'animal_name': 'Rex',
            'tutor_name': 'João Silva'
        }
    ]

    return jsonify({'appointments': appointments})