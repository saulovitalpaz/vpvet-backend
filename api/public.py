from flask import Blueprint, request, jsonify
from datetime import datetime

public_bp = Blueprint('public', __name__, url_prefix='/api/public')

@public_bp.route('/results', methods=['POST'])
def get_results():
    """
    Public endpoint to access exam results
    Requires CPF and access code
    """
    from models.exam import ExamResult
    from models.patient import Tutor
    from extensions import db

    data = request.get_json()

    if not data or not data.get('cpf') or not data.get('access_code'):
        return jsonify({'error': 'CPF and access code required'}), 400

    cpf = data['cpf'].replace('.', '').replace('-', '')  # Normalize CPF
    access_code = data['access_code'].upper().strip()

    # Find the exam result by access code
    exam_result = ExamResult.query.filter_by(access_code=access_code).first()

    if not exam_result:
        return jsonify({'error': 'Invalid access code'}), 404

    # Verify CPF matches the animal's tutor
    if not exam_result.animal or not exam_result.animal.tutor:
        return jsonify({'error': 'Result not found'}), 404

    tutor_cpf = exam_result.animal.tutor.cpf.replace('.', '').replace('-', '')

    if tutor_cpf != cpf:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Update last accessed timestamp
    exam_result.last_accessed = datetime.utcnow()
    db.session.commit()

    # Return public result
    return jsonify({
        'result': exam_result.to_public_dict(include_animal=True),
        'tutor': {
            'name': exam_result.animal.tutor.name
        }
    }), 200

@public_bp.route('/results/verify', methods=['POST'])
def verify_access():
    """
    Verify if CPF and access code combination exists
    """
    from models.exam import ExamResult
    from models.patient import Tutor

    data = request.get_json()

    if not data or not data.get('cpf') or not data.get('access_code'):
        return jsonify({'error': 'CPF and access code required'}), 400

    cpf = data['cpf'].replace('.', '').replace('-', '')
    access_code = data['access_code'].upper().strip()

    # Find the exam result
    exam_result = ExamResult.query.filter_by(access_code=access_code).first()

    if not exam_result or not exam_result.animal or not exam_result.animal.tutor:
        return jsonify({'valid': False}), 200

    tutor_cpf = exam_result.animal.tutor.cpf.replace('.', '').replace('-', '')

    return jsonify({
        'valid': tutor_cpf == cpf,
        'exam_type': exam_result.exam_type if tutor_cpf == cpf else None
    }), 200
