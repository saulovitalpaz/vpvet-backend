"""Patient management endpoints"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

patients_bp = Blueprint('patients', __name__, url_prefix='/api/patients')

@patients_bp.route('/tutors', methods=['GET'])
@jwt_required()
def get_tutors():
    """Get all tutors for testing"""
    # Mock data for testing
    tutors = [
        {
            'id': '1',
            'name': 'João Silva',
            'email': 'joao@example.com',
            'phone': '11999999999',
            'cpf': '12345678900',
            'address': 'Rua A, 123 - São Paulo, SP',
            'animals': [
                {
                    'id': '1',
                    'name': 'Rex',
                    'species': 'Cão',
                    'breed': 'Vira-lata'
                }
            ]
        },
        {
            'id': '2',
            'name': 'Maria Santos',
            'email': 'maria@example.com',
            'phone': '11988888888',
            'cpf': '98765432100',
            'address': 'Rua B, 456 - São Paulo, SP',
            'animals': [
                {
                    'id': '2',
                    'name': 'Mimi',
                    'species': 'Gato',
                    'breed': 'Siames'
                }
            ]
        }
    ]

    return jsonify({'tutors': tutors})