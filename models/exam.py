from extensions import db
from models.base import BaseModel
from sqlalchemy import Column, String, ForeignKey, Text, Date, DateTime, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import secrets

class Consultation(db.Model, BaseModel):
    __tablename__ = 'consultations'

    appointment_id = Column(UUID(as_uuid=True), ForeignKey('appointments.id'), nullable=False, unique=True)
    chief_complaint = Column(Text)
    physical_exam = Column(Text)
    diagnosis = Column(Text)
    prognosis = Column(String(50))
    treatment_plan = Column(Text)
    notes = Column(Text)

    # Relationships
    appointment = relationship('Appointment', backref='consultation')
    exam_results = relationship('ExamResult', back_populates='consultation')

    def to_dict(self):
        return {
            'id': str(self.id),
            'appointment_id': str(self.appointment_id),
            'chief_complaint': self.chief_complaint,
            'physical_exam': self.physical_exam,
            'diagnosis': self.diagnosis,
            'prognosis': self.prognosis,
            'treatment_plan': self.treatment_plan,
            'notes': self.notes
        }

class ExamResult(db.Model, BaseModel):
    __tablename__ = 'exam_results'

    consultation_id = Column(UUID(as_uuid=True), ForeignKey('consultations.id'), nullable=False)
    animal_id = Column(UUID(as_uuid=True), ForeignKey('animals.id'), nullable=False)
    exam_type = Column(String(100), nullable=False)
    access_code = Column(String(20), nullable=False, unique=True)
    findings = Column(Text, nullable=False)
    impression = Column(Text, nullable=False)
    pdf_url = Column(Text)
    images_url = Column(ARRAY(Text))
    exam_date = Column(Date, nullable=False)
    last_accessed = Column(DateTime)

    # Relationships
    consultation = relationship('Consultation', back_populates='exam_results')
    animal = relationship('Animal')

    @staticmethod
    def generate_access_code():
        """Generate a random 8-character access code"""
        return secrets.token_urlsafe(6).upper()[:8]

    def to_dict(self, include_sensitive=False):
        result = {
            'id': str(self.id),
            'exam_type': self.exam_type,
            'exam_date': self.exam_date.isoformat(),
            'findings': self.findings,
            'impression': self.impression,
            'pdf_url': self.pdf_url,
            'images_url': self.images_url or []
        }

        if include_sensitive:
            result['access_code'] = self.access_code
            result['consultation_id'] = str(self.consultation_id)
            result['animal_id'] = str(self.animal_id)
            result['last_accessed'] = self.last_accessed.isoformat() if self.last_accessed else None

        return result

    def to_public_dict(self, include_animal=False):
        """Public-facing dict for results portal"""
        result = {
            'exam_type': self.exam_type,
            'exam_date': self.exam_date.isoformat(),
            'findings': self.findings,
            'impression': self.impression,
            'pdf_url': self.pdf_url,
            'images_url': self.images_url or []
        }

        if include_animal and self.animal:
            result['animal'] = {
                'name': self.animal.name,
                'species': self.animal.species,
                'breed': self.animal.breed
            }

        return result
