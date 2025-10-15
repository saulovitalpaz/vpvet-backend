from extensions import db
from models.base import BaseModel
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class Tutor(db.Model, BaseModel):
    __tablename__ = 'tutors'

    name = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)

    # Relationships
    animals = relationship('Animal', back_populates='tutor')

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'cpf': self.cpf,
            'phone': self.phone,
            'email': self.email,
            'address': self.address
        }

class Animal(db.Model, BaseModel):
    __tablename__ = 'animals'

    tutor_id = Column(UUID(as_uuid=True), ForeignKey('tutors.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    species = Column(String(50), nullable=False)
    breed = Column(String(100))
    birth_date = Column(Date)
    sex = Column(String(10))
    weight = Column(Numeric(5, 2))
    is_neutered = Column(Boolean, default=False)
    microchip = Column(String(50))
    notes = Column(Text)

    # Relationships
    tutor = relationship('Tutor', back_populates='animals')
    appointments = relationship('Appointment', back_populates='animal')

    def to_dict(self):
        from datetime import date

        # Calculate age if birth_date exists
        age_years = None
        if self.birth_date:
            today = date.today()
            age_years = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

        return {
            'id': str(self.id),
            'name': self.name,
            'species': self.species,
            'breed': self.breed,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'age_years': age_years,
            'sex': self.sex,
            'weight': float(self.weight) if self.weight else None,
            'is_neutered': self.is_neutered,
            'microchip': self.microchip,
            'notes': self.notes,
            'tutor': self.tutor.to_dict() if self.tutor else None
        }

    def to_dict_with_tutor(self):
        return self.to_dict()
