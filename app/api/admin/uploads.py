from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from models.exam import ExamResult, Consultation
from models.patient import Animal
from models.appointment import Appointment
from extensions import db
import os
import uuid
import secrets
from datetime import datetime
from . import admin_bp, admin_required

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf': {'pdf'},
    'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
}

def allowed_file(filename, category):
    """Check if file has allowed extension"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(category, set())

def generate_access_code():
    """Generate unique 8-character access code"""
    while True:
        code = secrets.token_urlsafe(6)[:8]
        if not ExamResult.query.filter_by(access_code=code).first():
            return code

@admin_bp.route('/uploads/exam-note', methods=['POST'])
@admin_required
def upload_exam_note():
    """Upload exam note PDF and link to an animal/consultation"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400

        file = request.files['file']
        if file.filename == '':
            return {'error': 'No file selected'}, 400

        # Get form data
        consultation_id = request.form.get('consultation_id')
        animal_id = request.form.get('animal_id')
        exam_type = request.form.get('exam_type', 'Exame')
        findings = request.form.get('findings', '')
        impression = request.form.get('impression', '')

        if not consultation_id and not animal_id:
            return {'error': 'Either consultation_id or animal_id is required'}, 400

        # Validate file type
        if not allowed_file(file.filename, 'pdf'):
            return {'error': 'Only PDF files are allowed for exam notes'}, 400

        # Get consultation if provided
        consultation = None
        if consultation_id:
            consultation = Consultation.query.get(consultation_id)
            if not consultation:
                return {'error': 'Consultation not found'}, 404

        # Get animal
        animal = Animal.query.get(animal_id) if animal_id else None
        if not animal and consultation:
            # Get animal from consultation
            appointment = Appointment.query.get(consultation.appointment_id)
            animal = appointment.animal if appointment else None

        if not animal:
            return {'error': 'Animal not found'}, 404

        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'exam_notes')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)

        # Create exam result record
        exam_result = ExamResult(
            consultation_id=consultation_id,
            animal_id=animal.id,
            exam_type=exam_type,
            access_code=generate_access_code(),
            findings=findings,
            impression=impression,
            pdf_url=f"/uploads/exam_notes/{unique_filename}",
            exam_date=datetime.utcnow().date()
        )

        db.session.add(exam_result)
        db.session.commit()

        return {
            'message': 'Exam note uploaded successfully',
            'exam_result': {
                'id': str(exam_result.id),
                'access_code': exam_result.access_code,
                'exam_type': exam_type,
                'animal_name': animal.name,
                'pdf_url': exam_result.pdf_url,
                'exam_date': exam_result.exam_date.isoformat()
            }
        }, 201

    except Exception as e:
        db.session.rollback()
        # Clean up uploaded file if database transaction failed
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return {'error': 'Failed to upload exam note', 'details': str(e)}, 500

@admin_bp.route('/uploads/radiography', methods=['POST'])
@admin_required
def upload_radiography():
    """Upload radiography images and link to an animal/consultation"""
    try:
        # Check if files are in request
        if 'files' not in request.files:
            return {'error': 'No files provided'}, 400

        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return {'error': 'No files selected'}, 400

        # Get form data
        consultation_id = request.form.get('consultation_id')
        animal_id = request.form.get('animal_id')
        exam_type = request.form.get('exam_type', 'Radiografia')
        findings = request.form.get('findings', '')
        impression = request.form.get('impression', '')

        if not consultation_id and not animal_id:
            return {'error': 'Either consultation_id or animal_id is required'}, 400

        # Get consultation if provided
        consultation = None
        if consultation_id:
            consultation = Consultation.query.get(consultation_id)
            if not consultation:
                return {'error': 'Consultation not found'}, 404

        # Get animal
        animal = Animal.query.get(animal_id) if animal_id else None
        if not animal and consultation:
            # Get animal from consultation
            appointment = Appointment.query.get(consultation.appointment_id)
            animal = appointment.animal if appointment else None

        if not animal:
            return {'error': 'Animal not found'}, 404

        # Validate and save each file
        uploaded_files = []
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'radiographies')
        os.makedirs(upload_dir, exist_ok=True)

        for file in files:
            # Validate file type
            if not allowed_file(file.filename, 'image'):
                return {'error': f'Invalid file type: {file.filename}. Only images are allowed'}, 400

            # Save file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            uploaded_files.append(f"/uploads/radiographies/{unique_filename}")

        # Create exam result record
        exam_result = ExamResult(
            consultation_id=consultation_id,
            animal_id=animal.id,
            exam_type=exam_type,
            access_code=generate_access_code(),
            findings=findings,
            impression=impression,
            images_url=uploaded_files,
            exam_date=datetime.utcnow().date()
        )

        db.session.add(exam_result)
        db.session.commit()

        return {
            'message': f'{len(uploaded_files)} radiography images uploaded successfully',
            'exam_result': {
                'id': str(exam_result.id),
                'access_code': exam_result.access_code,
                'exam_type': exam_type,
                'animal_name': animal.name,
                'images_count': len(uploaded_files),
                'images_urls': uploaded_files,
                'exam_date': exam_result.exam_date.isoformat()
            }
        }, 201

    except Exception as e:
        db.session.rollback()
        # Clean up uploaded files if database transaction failed
        if 'uploaded_files' in locals():
            for file_url in uploaded_files:
                file_path = os.path.join(current_app.instance_path, file_url.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
        return {'error': 'Failed to upload radiography', 'details': str(e)}, 500

@admin_bp.route('/uploads/bulk', methods=['POST'])
@admin_required
def bulk_upload_records():
    """Bulk upload multiple exam notes and radiographies"""
    try:
        # Get JSON data with metadata
        metadata = request.get_json()
        records = metadata.get('records', [])

        if not records:
            return {'error': 'No records provided'}, 400

        results = []
        errors = []

        for i, record in enumerate(records):
            try:
                # For each record, you would need to process the actual files
                # This is a simplified version - you'd need to handle file uploads properly
                # in a real implementation with proper file handling

                # Validate required fields
                if not record.get('animal_id'):
                    errors.append(f"Record {i+1}: animal_id is required")
                    continue

                animal = Animal.query.get(record['animal_id'])
                if not animal:
                    errors.append(f"Record {i+1}: Animal not found")
                    continue

                # Create exam result (simplified - assumes files are already uploaded)
                exam_result = ExamResult(
                    consultation_id=record.get('consultation_id'),
                    animal_id=animal.id,
                    exam_type=record.get('exam_type', 'Exame'),
                    access_code=generate_access_code(),
                    findings=record.get('findings', ''),
                    impression=record.get('impression', ''),
                    pdf_url=record.get('pdf_url', ''),
                    images_url=record.get('images_urls', []),
                    exam_date=datetime.strptime(record['exam_date'], '%Y-%m-%d').date() if record.get('exam_date') else datetime.utcnow().date()
                )

                db.session.add(exam_result)
                results.append({
                    'index': i+1,
                    'access_code': exam_result.access_code,
                    'animal_name': animal.name
                })

            except Exception as e:
                errors.append(f"Record {i+1}: {str(e)}")
                continue

        if results:
            db.session.commit()

        return {
            'message': f'Processed {len(results)} records successfully',
            'uploaded': results,
            'errors': errors
        }, 200 if results else 400

    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to process bulk upload', 'details': str(e)}, 500

@admin_bp.route('/uploads/record/<record_id>', methods=['GET'])
@admin_required
def get_upload_record(record_id):
    """Get details of an uploaded exam record"""
    try:
        exam_result = ExamResult.query.get_or_404(record_id)

        # Get animal and consultation info
        animal = Animal.query.get(exam_result.animal_id)
        consultation = None
        if exam_result.consultation_id:
            consultation = Consultation.query.get(exam_result.consultation_id)
            if consultation:
                appointment = Appointment.query.get(consultation.appointment_id)
                consultation = {
                    'id': str(consultation.id),
                    'appointment_datetime': appointment.datetime.isoformat() if appointment else None,
                    'chief_complaint': consultation.chief_complaint
                }

        return jsonify({
            'id': str(exam_result.id),
            'access_code': exam_result.access_code,
            'exam_type': exam_result.exam_type,
            'exam_date': exam_result.exam_date.isoformat() if exam_result.exam_date else None,
            'findings': exam_result.findings,
            'impression': exam_result.impression,
            'pdf_url': exam_result.pdf_url,
            'images_urls': exam_result.images_url or [],
            'animal': {
                'id': str(animal.id),
                'name': animal.name,
                'species': animal.species,
                'breed': animal.breed
            } if animal else None,
            'consultation': consultation,
            'last_accessed': exam_result.last_accessed.isoformat() if exam_result.last_accessed else None,
            'created_at': exam_result.created_at.isoformat() if exam_result.created_at else None
        }), 200

    except Exception as e:
        return {'error': 'Failed to fetch upload record', 'details': str(e)}, 500