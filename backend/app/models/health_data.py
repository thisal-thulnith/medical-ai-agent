from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Date, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class SeverityLevel(str, enum.Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"
    critical = "critical"


class VitalSignType(str, enum.Enum):
    blood_pressure = "blood_pressure"
    heart_rate = "heart_rate"
    temperature = "temperature"
    weight = "weight"
    height = "height"
    blood_glucose = "blood_glucose"
    oxygen_saturation = "oxygen_saturation"
    respiratory_rate = "respiratory_rate"


class ReportType(str, enum.Enum):
    blood_test = "blood_test"
    imaging = "imaging"
    pathology = "pathology"
    ecg = "ecg"
    prescription = "prescription"
    discharge_summary = "discharge_summary"
    other = "other"


class MemoryType(str, enum.Enum):
    medical_history = "medical_history"
    preference = "preference"
    conversation_context = "conversation_context"
    health_goal = "health_goal"


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    symptom_name = Column(String, nullable=False, index=True)
    severity = Column(Enum(SeverityLevel), nullable=True)
    body_part = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    duration_days = Column(Integer, nullable=True)
    photo_url = Column(String, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="symptoms")


class VitalSign(Base):
    __tablename__ = "vital_signs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    type = Column(Enum(VitalSignType), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="vital_signs")


class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    name = Column(String, nullable=False, index=True)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    prescribed_by = Column(String, nullable=True)
    purpose = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="medications")


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    file_url = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    parsed_data = Column(JSON, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    report_date = Column(Date, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="medical_reports")


class HealthCondition(Base):
    __tablename__ = "health_conditions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    condition_name = Column(String, nullable=False, index=True)
    diagnosed_date = Column(Date, nullable=True)
    status = Column(String, nullable=True)
    severity = Column(Enum(SeverityLevel), nullable=True)
    notes = Column(Text, nullable=True)
    icd_10_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="health_conditions")


class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    allergen = Column(String, nullable=False, index=True)
    severity = Column(Enum(SeverityLevel), nullable=False)
    reaction = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="allergies")


class UserMemory(Base):
    __tablename__ = "user_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    memory_type = Column(Enum(MemoryType), nullable=False)
    content = Column(Text, nullable=False)
    embedding_id = Column(String, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="memories")
