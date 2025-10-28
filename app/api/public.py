"""Public access endpoints"""
from flask import Blueprint, request, jsonify

public_bp = Blueprint('public', __name__, url_prefix='/api/public')

@public_bp.route('/results', methods=['POST'])
def get_results():
    """Public endpoint to access exam results"""
    data = request.get_json()

    if not data or not data.get('cpf') or not data.get('access_code'):
        return jsonify({'error': 'CPF and access code required'}), 400

    # Mock validation
    # In production, this should validate against database
    if data.get('cpf') == '12345678900' and data.get('access_code') == 'ABC12345':
        return jsonify({
            'results': [
                {
                    'exam_type': 'Hemograma Completo',
                    'exam_date': '2025-10-20',
                    'findings': 'Todos os parâmetros dentro dos valores de referência',
                    'impression': 'Não há indicações de patologia'
                }
            ],
            'patient_name': 'Paciente Teste',
            'animal_name': 'Rex'
        }), 200

    return jsonify({'error': 'Invalid CPF or access code'}), 401

@public_bp.route('/results/verify', methods=['POST'])
def verify_access_code():
    """Verify if access code is valid"""
    data = request.get_json()
    access_code = data.get('access_code')

    if access_code == 'ABC12345':
        return jsonify({'valid': True}), 200
    else:
        return jsonify({'valid': False}), 404