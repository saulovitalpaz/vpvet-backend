from flask import request, jsonify
from models.patient import Tutor, Animal
from models.appointment import Appointment
from models.exam import Consultation
from extensions import db
from . import admin_bp, admin_required
from datetime import datetime
from sqlalchemy import or_, and_

@admin_bp.route('/clients', methods=['GET'])
@admin_required
def get_all_clients():
    """Get all clients (tutors) across all clinics"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        clinic_id = request.args.get('clinic_id', '')

        # Build query
        query = Tutor.query

        # Apply search filter
        if search:
            query = query.filter(
                Tutor.name.ilike(f'%{search}%') |
                Tutor.email.ilike(f'%{search}%') |
                Tutor.cpf.ilike(f'%{search}%')
            )

        # Order by created date
        query = query.order_by(Tutor.created_at.desc())

        # Paginate
        tutors = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        tutors_data = []
        for tutor in tutors.items:
            # Count animals
            animal_count = Animal.query.filter_by(tutor_id=tutor.id).count()

            # Get last appointment date
            last_appointment = Appointment.query.join(Animal).filter(
                Animal.tutor_id == tutor.id
            ).order_by(Appointment.datetime.desc()).first()

            # Count total appointments
            appointment_count = Appointment.query.join(Animal).filter(
                Animal.tutor_id == tutor.id
            ).count()

            tutors_data.append({
                'id': str(tutor.id),
                'name': tutor.name,
                'email': tutor.email,
                'phone': tutor.phone,
                'cpf': tutor.cpf,
                'address': tutor.address,
                'animal_count': animal_count,
                'appointment_count': appointment_count,
                'last_appointment': last_appointment.datetime.isoformat() if last_appointment else None,
                'created_at': tutor.created_at.isoformat() if tutor.created_at else None
            })

        return jsonify({
            'clients': tutors_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': tutors.total,
                'pages': tutors.pages,
                'has_next': tutors.has_next,
                'has_prev': tutors.has_prev
            }
        }), 200

    except Exception as e:
        return {'error': 'Failed to fetch clients', 'details': str(e)}, 500

@admin_bp.route('/clients', methods=['POST'])
@admin_required
def create_client():
    """Create a new client (tutor)"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'cpf', 'phone']
        for field in required_fields:
            if field not in data:
                return {'error': f'{field} is required'}, 400

        # Check if CPF already exists
        if Tutor.query.filter_by(cpf=data['cpf']).first():
            return {'error': 'A client with this CPF already exists'}, 400

        # Check if email already exists (if provided)
        if data.get('email') and Tutor.query.filter_by(email=data['email']).first():
            return {'error': 'A client with this email already exists'}, 400

        # Create new tutor
        tutor = Tutor(
            name=data['name'],
            cpf=data['cpf'],
            phone=data['phone'],
            email=data.get('email', ''),
            address=data.get('address', '')
        )

        db.session.add(tutor)
        db.session.commit()

        # Add animals if provided
        if 'animals' in data and data['animals']:
            for animal_data in data['animals']:
                animal = Animal(
                    tutor_id=tutor.id,
                    name=animal_data['name'],
                    species=animal_data.get('species', ''),
                    breed=animal_data.get('breed', ''),
                    birth_date=datetime.strptime(animal_data['birth_date'], '%Y-%m-%d').date() if animal_data.get('birth_date') else None,
                    sex=animal_data.get('sex', ''),
                    weight=animal_data.get('weight'),
                    is_neutered=animal_data.get('is_neutered', False),
                    microchip=animal_data.get('microchip', ''),
                    notes=animal_data.get('notes', '')
                )
                db.session.add(animal)

            db.session.commit()

        return {
            'message': 'Client created successfully',
            'client': {
                'id': str(tutor.id),
                'name': tutor.name,
                'email': tutor.email,
                'phone': tutor.phone,
                'cpf': tutor.cpf,
                'address': tutor.address
            }
        }, 201

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to create client', 'details': str(e)}, 500

@admin_bp.route('/clients/<client_id>', methods=['GET'])
@admin_required
def get_client_details(client_id):
    """Get detailed information about a client including their animals"""
    try:
        tutor = Tutor.query.get_or_404(client_id)

        # Get all animals for this tutor
        animals = Animal.query.filter_by(tutor_id=client_id).all()
        animals_data = []

        for animal in animals:
            # Get appointment count for this animal
            appointment_count = Appointment.query.filter_by(animal_id=animal.id).count()

            # Get last appointment
            last_appointment = Appointment.query.filter_by(animal_id=animal.id).order_by(
                Appointment.datetime.desc()
            ).first()

            # Get last consultation
            last_consultation = Consultation.query.join(Appointment).filter(
                Appointment.animal_id == animal.id
            ).order_by(Consultation.created_at.desc()).first()

            animals_data.append({
                'id': str(animal.id),
                'name': animal.name,
                'species': animal.species,
                'breed': animal.breed,
                'sex': animal.sex,
                'weight': animal.weight,
                'is_neutered': animal.is_neutered,
                'microchip': animal.microchip,
                'birth_date': animal.birth_date.isoformat() if animal.birth_date else None,
                'notes': animal.notes,
                'appointment_count': appointment_count,
                'last_appointment': last_appointment.datetime.isoformat() if last_appointment else None,
                'last_consultation': {
                    'id': str(last_consultation.id),
                    'created_at': last_consultation.created_at.isoformat() if last_consultation.created_at else None
                } if last_consultation else None
            })

        # Get recent appointments for all animals of this tutor
        recent_appointments = Appointment.query.join(Animal).filter(
            Animal.tutor_id == client_id
        ).order_by(Appointment.datetime.desc()).limit(10).all()

        appointments_data = []
        for apt in recent_appointments:
            appointments_data.append({
                'id': str(apt.id),
                'datetime': apt.datetime.isoformat(),
                'clinic_id': str(apt.clinic_id),
                'clinic_name': apt.clinic.name if apt.clinic else None,
                'animal_name': apt.animal.name,
                'service_type': apt.service_type,
                'status': apt.status,
                'duration_minutes': apt.duration_minutes
            })

        return jsonify({
            'id': str(tutor.id),
            'name': tutor.name,
            'email': tutor.email,
            'phone': tutor.phone,
            'cpf': tutor.cpf,
            'address': tutor.address,
            'created_at': tutor.created_at.isoformat() if tutor.created_at else None,
            'animals': animals_data,
            'recent_appointments': appointments_data
        }), 200

    except Exception as e:
        return {'error': 'Failed to fetch client details', 'details': str(e)}, 500

@admin_bp.route('/clients/<client_id>', methods=['PUT'])
@admin_required
def update_client(client_id):
    """Update client information"""
    try:
        tutor = Tutor.query.get_or_404(client_id)
        data = request.get_json()

        # Update fields
        if 'name' in data:
            tutor.name = data['name']
        if 'email' in data:
            # Check if email already exists for another tutor
            existing = Tutor.query.filter(Tutor.email == data['email'], Tutor.id != client_id).first()
            if existing:
                return {'error': 'Another client with this email already exists'}, 400
            tutor.email = data['email']
        if 'phone' in data:
            tutor.phone = data['phone']
        if 'cpf' in data:
            # Check if CPF already exists for another tutor
            existing = Tutor.query.filter(Tutor.cpf == data['cpf'], Tutor.id != client_id).first()
            if existing:
                return {'error': 'Another client with this CPF already exists'}, 400
            tutor.cpf = data['cpf']
        if 'address' in data:
            tutor.address = data['address']

        db.session.commit()

        return {
            'message': 'Client updated successfully',
            'client': {
                'id': str(tutor.id),
                'name': tutor.name,
                'email': tutor.email,
                'phone': tutor.phone,
                'cpf': tutor.cpf,
                'address': tutor.address
            }
        }, 200

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to update client', 'details': str(e)}, 500

@admin_bp.route('/clients/<client_id>/animals', methods=['POST'])
@admin_required
def add_client_animal(client_id):
    """Add a new animal to a client"""
    try:
        tutor = Tutor.query.get_or_404(client_id)
        data = request.get_json()

        # Validate required fields
        if 'name' not in data:
            return {'error': 'Animal name is required'}, 400

        animal = Animal(
            tutor_id=tutor.id,
            name=data['name'],
            species=data.get('species', ''),
            breed=data.get('breed', ''),
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
            sex=data.get('sex', ''),
            weight=data.get('weight'),
            is_neutered=data.get('is_neutered', False),
            microchip=data.get('microchip', ''),
            notes=data.get('notes', '')
        )

        db.session.add(animal)
        db.session.commit()

        return {
            'message': 'Animal added successfully',
            'animal': {
                'id': str(animal.id),
                'name': animal.name,
                'species': animal.species,
                'breed': animal.breed,
                'sex': animal.sex,
                'weight': animal.weight,
                'is_neutered': animal.is_neutered,
                'microchip': animal.microchip,
                'birth_date': animal.birth_date.isoformat() if animal.birth_date else None,
                'notes': animal.notes
            }
        }, 201

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to add animal', 'details': str(e)}, 500