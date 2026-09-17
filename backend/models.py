from database import Base
from enum import Enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Date, Enum as SQLEnum, ForeignKey, UniqueConstraint, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class RoleEnum(str, Enum):
    """User role enumeration"""
    DOCTOR = "doctor"
    TECHNICAL_STAFF = "technical_staff"
    ADMIN = "admin"

class SexEnum(str, Enum):
    """Patient sex enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class ScanStatusEnum(str, Enum):
    """Scan status enumeration"""
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"

class Hospital(Base):
    """Hospital model"""
    __tablename__ = 'hospitals'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    region = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    users = relationship('User', back_populates='hospital', cascade='all, delete-orphan')
    patients = relationship('Patient', back_populates='hospital', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Hospital {self.name}>'

class User(Base):
    """User model for doctors, technical staff, and admins"""
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), nullable=False)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey('hospitals.id'), nullable=False)
    specialty = Column(String(255), nullable=True)  # Relevant for doctors
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    hospital = relationship('Hospital', back_populates='users')
    scans = relationship('Scan', back_populates='uploaded_by', foreign_keys='Scan.uploaded_by_id')

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'

class Patient(Base):
    """Patient model"""
    __tablename__ = 'patients'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_code = Column(String(50), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    sex = Column(SQLEnum(SexEnum), nullable=False)
    phone_number = Column(String(8), nullable=False)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey('hospitals.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    hospital = relationship('Hospital', back_populates='patients')
    scans = relationship('Scan', back_populates='patient', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Patient {self.patient_code} - {self.full_name}>'

class Scan(Base):
    """Retinal scan model"""
    __tablename__ = 'scans'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=False)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    file_path = Column(String(500), nullable=False)
    ai_grade = Column(Integer, nullable=False)  # 0-4: No DR to Proliferative DR
    ai_confidence = Column(Float, nullable=False)  # 0-1
    ai_severity = Column(String(50), nullable=False)  # Human-readable severity
    status = Column(SQLEnum(ScanStatusEnum), nullable=False, default=ScanStatusEnum.PENDING_REVIEW)
    doctor_grade = Column(Integer, nullable=True)  # Doctor's assessment (after review)
    doctor_notes = Column(String(1000), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    patient = relationship('Patient', back_populates='scans', foreign_keys=[patient_id])
    uploaded_by = relationship('User', back_populates='scans', foreign_keys=[uploaded_by_id])
    reviewed_by = relationship('User', foreign_keys=[reviewed_by_id])

    def __repr__(self):
        return f'<Scan {self.id} - Patient {self.patient_id} - Grade {self.ai_grade}>'
