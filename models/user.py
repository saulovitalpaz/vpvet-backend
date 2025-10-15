from extensions import db
from models.base import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class Clinic(db.Model, BaseModel):
    __tablename__ = 'clinics'

    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)

    # Relationships
    users = relationship('User', back_populates='clinic')
    appointments = relationship('Appointment', back_populates='clinic')

class User(db.Model, BaseModel):
    __tablename__ = 'users'

    clinic_id = Column(UUID(as_uuid=True), ForeignKey('clinics.id'))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='secretary')
    is_active = Column(Boolean, default=True)

    # Relationships
    clinic = relationship('Clinic', back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_dr_saulo(self):
        return self.role == 'dr_saulo'

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_dr_saulo': self.is_dr_saulo,
            'clinic': {
                'id': str(self.clinic.id),
                'name': self.clinic.name
            } if self.clinic else None
        }
