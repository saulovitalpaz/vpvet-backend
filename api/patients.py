from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

patients_bp = Blueprint('patients', __name__, url_prefix='/api/patients')

@patients_bp.route('/tutors', methods=['GET'])
@jwt_required()
def get_tutors():
    from models.patient import Tutor

    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Tutor.query

    if search:
        query = query.filter(
            (Tutor.name.ilike(f'%{search}%')) |
            (Tutor.cpf.ilike(f'%{search}%'))
        )

    paginated = query.order_by(Tutor.name).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'tutors': [tutor.to_dict() for tutor in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@patients_bp.route('/tutors', methods=['POST'])
@jwt_required()
def create_tutor():
    from models.patient import Tutor
    from extensions import db

    data = request.get_json()

    required = ['name', 'cpf']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if CPF already exists
    existing = Tutor.query.filter_by(cpf=data['cpf']).first()
    if existing:
        return jsonify({'error': 'CPF already registered'}), 409

    tutor = Tutor(
        name=data['name'],
        cpf=data['cpf'],
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address')
    )

    db.session.add(tutor)
    db.session.commit()

    return jsonify({'tutor': tutor.to_dict()}), 201

@patients_bp.route('/tutors/<tutor_id>', methods=['GET'])
@jwt_required()
def get_tutor(tutor_id):
    from models.patient import Tutor

    tutor = Tutor.query.get(tutor_id)

    if not tutor:
        return jsonify({'error': 'Tutor not found'}), 404

    return jsonify({'tutor': tutor.to_dict()}), 200

@patients_bp.route('/animals', methods=['GET'])
@jwt_required()
def get_animals():
    from models.patient import Animal

    search = request.args.get('search', '')
    tutor_id = request.args.get('tutor_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Animal.query

    if search:
        query = query.filter(Animal.name.ilike(f'%{search}%'))

    if tutor_id:
        query = query.filter_by(tutor_id=tutor_id)

    paginated = query.order_by(Animal.name).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'animals': [animal.to_dict() for animal in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@patients_bp.route('/animals', methods=['POST'])
@jwt_required()
def create_animal():
    from models.patient import Animal
    from extensions import db
    from datetime import datetime

    data = request.get_json()

    required = ['tutor_id', 'name', 'species']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    animal = Animal(
        tutor_id=data['tutor_id'],
        name=data['name'],
        species=data['species'],
        breed=data.get('breed'),
        birth_date=datetime.fromisoformat(data['birth_date']) if data.get('birth_date') else None,
        sex=data.get('sex'),
        weight=data.get('weight'),
        is_neutered=data.get('is_neutered', False),
        microchip=data.get('microchip'),
        notes=data.get('notes')
    )

    db.session.add(animal)
    db.session.commit()

    return jsonify({'animal': animal.to_dict()}), 201

@patients_bp.route('/animals/<animal_id>', methods=['GET'])
@jwt_required()
def get_animal(animal_id):
    from models.patient import Animal

    animal = Animal.query.get(animal_id)

    if not animal:
        return jsonify({'error': 'Animal not found'}), 404

    return jsonify({'animal': animal.to_dict()}), 200

@patients_bp.route('/animals/<animal_id>', methods=['PUT'])
@jwt_required()
def update_animal(animal_id):
    from models.patient import Animal
    from extensions import db
    from datetime import datetime

    animal = Animal.query.get(animal_id)

    if not animal:
        return jsonify({'error': 'Animal not found'}), 404

    data = request.get_json()

    # Update fields
    if 'name' in data:
        animal.name = data['name']
    if 'species' in data:
        animal.species = data['species']
    if 'breed' in data:
        animal.breed = data['breed']
    if 'birth_date' in data:
        animal.birth_date = datetime.fromisoformat(data['birth_date']) if data['birth_date'] else None
    if 'sex' in data:
        animal.sex = data['sex']
    if 'weight' in data:
        animal.weight = data['weight']
    if 'is_neutered' in data:
        animal.is_neutered = data['is_neutered']
    if 'microchip' in data:
        animal.microchip = data['microchip']
    if 'notes' in data:
        animal.notes = data['notes']

    db.session.commit()

    return jsonify({'animal': animal.to_dict()}), 200

@patients_bp.route('/animals/<animal_id>', methods=['DELETE'])
@jwt_required()
def delete_animal(animal_id):
    from models.patient import Animal
    from extensions import db

    animal = Animal.query.get(animal_id)

    if not animal:
        return jsonify({'error': 'Animal not found'}), 404

    db.session.delete(animal)
    db.session.commit()

    return jsonify({'message': 'Animal deleted successfully'}), 200

@patients_bp.route('/animals/<animal_id>/consultations', methods=['GET'])
@jwt_required()
def get_animal_consultations(animal_id):
    from models.patient import Animal
    from models.appointment import Appointment
    from models.exam import Consultation

    animal = Animal.query.get(animal_id)

    if not animal:
        return jsonify({'error': 'Animal not found'}), 404

    # Get all consultations for this animal through appointments
    consultations = Consultation.query.join(Appointment).filter(
        Appointment.animal_id == animal_id
    ).order_by(Appointment.datetime.desc()).all()

    return jsonify({
        'consultations': [{
            'id': str(c.id),
            'appointment_id': str(c.appointment_id),
            'chief_complaint': c.chief_complaint,
            'diagnosis': c.diagnosis,
            'treatment_plan': c.treatment_plan,
            'appointment': {
                'datetime': c.appointment.datetime.isoformat(),
                'service_type': c.appointment.service_type
            },
            'created_at': c.created_at.isoformat()
        } for c in consultations]
    }), 200

@patients_bp.route('', methods=['GET'])
@patients_bp.route('/', methods=['GET'])
@jwt_required()
def get_patients():
    from models.patient import Animal, Tutor
    from sqlalchemy.orm import joinedload

    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)

    query = Animal.query.options(joinedload(Animal.tutor))

    if search:
        query = query.join(Tutor).filter(
            (Animal.name.ilike(f'%{search}%')) |
            (Tutor.name.ilike(f'%{search}%')) |
            (Tutor.cpf.ilike(f'%{search}%'))
        )

    patients = query.order_by(Animal.name).limit(limit).all()

    return jsonify({
        'patients': [animal.to_dict_with_tutor() for animal in patients]
    }), 200

@patients_bp.route('', methods=['POST'])
@patients_bp.route('/', methods=['POST'])
@jwt_required()
def create_patient():
    from models.patient import Tutor, Animal
    from extensions import db
    from datetime import datetime

    data = request.get_json()

    # Validate required fields
    if 'tutor' not in data or 'animal' not in data:
        return jsonify({'error': 'Missing tutor or animal data'}), 400

    tutor_data = data['tutor']
    animal_data = data['animal']

    # Check required tutor fields
    if not all(field in tutor_data for field in ['cpf', 'name', 'phone']):
        return jsonify({'error': 'Missing required tutor fields'}), 400

    # Check required animal fields
    if not all(field in animal_data for field in ['name', 'species', 'sex']):
        return jsonify({'error': 'Missing required animal fields'}), 400

    # Check if tutor already exists by CPF
    tutor = Tutor.query.filter_by(cpf=tutor_data['cpf']).first()

    if not tutor:
        # Create new tutor
        tutor = Tutor(
            cpf=tutor_data['cpf'],
            name=tutor_data['name'],
            phone=tutor_data['phone'],
            email=tutor_data.get('email'),
            address=tutor_data.get('address')
        )
        db.session.add(tutor)
        db.session.flush()  # Get tutor ID without committing

    # Create animal
    animal = Animal(
        tutor_id=tutor.id,
        name=animal_data['name'],
        species=animal_data['species'],
        breed=animal_data.get('breed'),
        birth_date=datetime.fromisoformat(animal_data['birth_date']) if animal_data.get('birth_date') else None,
        sex=animal_data['sex'],
        weight=animal_data.get('weight'),
        is_neutered=animal_data.get('is_neutered', False),
        microchip=animal_data.get('microchip'),
        notes=animal_data.get('notes')
    )

    db.session.add(animal)
    db.session.commit()

    return jsonify({
        'patient': animal.to_dict_with_tutor()
    }), 201
