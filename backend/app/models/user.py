from sqlalchemy import Column, Integer, String, DateTime, Date, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    phone_number = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    blood_type = Column(String, nullable=True)
    height_cm = Column(Integer, nullable=True)
    weight_kg = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    symptoms = relationship("Symptom", back_populates="user", cascade="all, delete-orphan")
    vital_signs = relationship("VitalSign", back_populates="user", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="user", cascade="all, delete-orphan")
    medical_reports = relationship("MedicalReport", back_populates="user", cascade="all, delete-orphan")
    health_conditions = relationship("HealthCondition", back_populates="user", cascade="all, delete-orphan")
    allergies = relationship("Allergy", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("UserMemory", back_populates="user", cascade="all, delete-orphan")
