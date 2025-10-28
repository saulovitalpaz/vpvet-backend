"""Consultation endpoints"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

consultations_bp = Blueprint('consultations', __name__, url_prefix='/api/consultations')

@consultations_bp.route('/', methods=['GET'])
@jwt_required()
def get_consultations():
    """Get all consultations for current user"""
    current_user = get_jwt_identity()

    # Mock consultations
    consultations = [
        {
            'id': '1',
            'appointment_id': '1',
            'chief_complaint': 'Animal com dor',
            'physical_exam': ' Paciente alerta, responsivo, hidratado. Mucosas rosadas.',
            'diagnosis': 'Dermatite alérgica',
            'treatment_plan': 'Antibióticos e pomadas tópicas',
            'notes': 'Retorno em 7 dias'
        }
    ]

    return jsonify({'consultations': consultations})