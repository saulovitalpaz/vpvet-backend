from extensions import db
from models.base import BaseModel
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class Appointment(db.Model, BaseModel):
    __tablename__ = 'appointments'

    clinic_id = Column(UUID(as_uuid=True), ForeignKey('clinics.id'), nullable=False)
    animal_id = Column(UUID(as_uuid=True), ForeignKey('animals.id'), nullable=False)
    datetime = Column(DateTime, nullable=False, unique=True)
    duration_minutes = Column(Integer, default=30)
    service_type = Column(String(100), nullable=False)
    status = Column(String(20), default='scheduled')
    notes = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    # Relationships
    clinic = relationship('Clinic', back_populates='appointments')
    animal = relationship('Animal', back_populates='appointments')
    creator = relationship('User')

    def to_dict(self, include_details=False):
        result = {
            'id': str(self.id),
            'datetime': self.datetime.isoformat(),
            'duration_minutes': self.duration_minutes,
            'status': self.status
        }

        if include_details:
            result.update({
                'service_type': self.service_type,
                'notes': self.notes,
                'clinic': {
                    'id': str(self.clinic.id),
                    'name': self.clinic.name
                },
                'animal': self.animal.to_dict() if self.animal else None
            })

        return result
