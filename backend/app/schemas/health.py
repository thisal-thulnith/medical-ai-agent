from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from app.models.health_data import SeverityLevel, VitalSignType, ReportType


class SymptomCreate(BaseModel):
    symptom_name: str
    severity: Optional[SeverityLevel] = None
    body_part: Optional[str] = None
    description: Optional[str] = None
    duration_days: Optional[int] = None


class SymptomResponse(BaseModel):
    id: int
    symptom_name: str
    severity: Optional[SeverityLevel]
    body_part: Optional[str]
    description: Optional[str]
    logged_at: datetime

    class Config:
        from_attributes = True


class VitalSignCreate(BaseModel):
    type: VitalSignType
    value: float
    unit: str
    notes: Optional[str] = None


class VitalSignResponse(BaseModel):
    id: int
    type: VitalSignType
    value: float
    unit: str
    recorded_at: datetime

    class Config:
        from_attributes = True


class MedicationCreate(BaseModel):
    name: str
    dosage: str
    frequency: str
    start_date: date
    end_date: Optional[date] = None
    purpose: Optional[str] = None


class MedicationResponse(BaseModel):
    id: int
    name: str
    dosage: str
    frequency: str
    start_date: date
    end_date: Optional[date]
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReportUpload(BaseModel):
    report_type: ReportType
    report_date: Optional[date] = None


class ReportResponse(BaseModel):
    id: int
    report_type: ReportType
    file_name: str
    ai_analysis: Optional[Dict[str, Any]]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class HealthConditionResponse(BaseModel):
    id: int
    condition_name: str
    status: Optional[str]
    severity: Optional[SeverityLevel]
    diagnosed_date: Optional[date]

    class Config:
        from_attributes = True


class AllergyResponse(BaseModel):
    id: int
    allergen: str
    severity: SeverityLevel
    reaction: Optional[str]

    class Config:
        from_attributes = True


class HealthDataResponse(BaseModel):
    symptoms: List[SymptomResponse]
    vital_signs: List[VitalSignResponse]
    medications: List[MedicationResponse]
    conditions: List[HealthConditionResponse]
    allergies: List[AllergyResponse]
    recent_reports: List[ReportResponse]


class DashboardStats(BaseModel):
    health_score: float
    total_symptoms: int
    active_medications: int
    recent_vitals_count: int
    pending_checkups: int
    risk_alerts: List[str]
