from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

consultations_bp = Blueprint('consultations', __name__, url_prefix='/api/consultations')

@consultations_bp.route('', methods=['GET'])
@consultations_bp.route('/', methods=['GET'])
@jwt_required()
def get_consultations():
    from models.exam import Consultation
    from models.appointment import Appointment
    from models.patient import Animal, Tutor
    from sqlalchemy.orm import joinedload

    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)

    query = Consultation.query.options(
        joinedload(Consultation.appointment).joinedload(Appointment.animal).joinedload(Animal.tutor)
    )

    if search:
        query = query.join(Appointment).join(Animal).join(Tutor).filter(
            (Animal.name.ilike(f'%{search}%')) |
            (Tutor.name.ilike(f'%{search}%')) |
            (Consultation.diagnosis.ilike(f'%{search}%')) |
            (Consultation.chief_complaint.ilike(f'%{search}%'))
        )
    else:
        # Need to join Appointment for ordering even without search
        query = query.join(Appointment)

    consultations = query.order_by(Appointment.datetime.desc()).limit(limit).all()

    return jsonify({
        'consultations': [{
            'id': str(c.id),
            'appointment_id': str(c.appointment_id),
            'chief_complaint': c.chief_complaint,
            'diagnosis': c.diagnosis,
            'treatment_plan': c.treatment_plan,
            'prognosis': c.prognosis,
            'created_at': c.created_at.isoformat(),
            'appointment': {
                'datetime': c.appointment.datetime.isoformat(),
                'service_type': c.appointment.service_type,
                'animal': {
                    'id': str(c.appointment.animal.id),
                    'name': c.appointment.animal.name,
                    'species': c.appointment.animal.species,
                    'tutor': {
                        'name': c.appointment.animal.tutor.name
                    }
                }
            }
        } for c in consultations]
    }), 200

@consultations_bp.route('/<consultation_id>', methods=['GET'])
@jwt_required()
def get_consultation(consultation_id):
    from models.exam import Consultation

    consultation = Consultation.query.get(consultation_id)

    if not consultation:
        return jsonify({'error': 'Consultation not found'}), 404

    return jsonify({
        'consultation': {
            'id': str(consultation.id),
            'appointment_id': str(consultation.appointment_id),
            'chief_complaint': consultation.chief_complaint,
            'physical_exam': consultation.physical_exam,
            'diagnosis': consultation.diagnosis,
            'prognosis': consultation.prognosis,
            'treatment_plan': consultation.treatment_plan,
            'notes': consultation.notes,
            'created_at': consultation.created_at.isoformat(),
            'appointment': {
                'datetime': consultation.appointment.datetime.isoformat(),
                'service_type': consultation.appointment.service_type,
                'status': consultation.appointment.status,
                'animal': {
                    'id': str(consultation.appointment.animal.id),
                    'name': consultation.appointment.animal.name,
                    'species': consultation.appointment.animal.species,
                    'breed': consultation.appointment.animal.breed,
                    'age_years': consultation.appointment.animal.to_dict().get('age_years'),
                    'sex': consultation.appointment.animal.sex,
                    'weight': float(consultation.appointment.animal.weight) if consultation.appointment.animal.weight else None,
                    'tutor': {
                        'name': consultation.appointment.animal.tutor.name,
                        'phone': consultation.appointment.animal.tutor.phone,
                        'email': consultation.appointment.animal.tutor.email
                    }
                }
            }
        }
    }), 200
