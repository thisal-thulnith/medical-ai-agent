"""
Dashboard API endpoints - Health data overview and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta, date

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.health_data import (
    Symptom, VitalSign, Medication,
    HealthCondition, Allergy, MedicalReport
)
from app.schemas.health import (
    HealthDataResponse, DashboardStats,
    SymptomResponse, VitalSignResponse, MedicationResponse,
    HealthConditionResponse, AllergyResponse, ReportResponse
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics and health score
    """
    # Calculate health score (simplified algorithm)
    health_score = 85.0  # Base score

    # Count recent symptoms (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_symptoms = db.query(Symptom).filter(
        Symptom.user_id == current_user.id,
        Symptom.logged_at >= seven_days_ago
    ).count()

    # Reduce score based on symptoms
    health_score -= min(recent_symptoms * 3, 20)

    # Count active medications
    active_meds = db.query(Medication).filter(
        Medication.user_id == current_user.id,
        Medication.is_active == 1
    ).count()

    # Count recent vitals (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_vitals = db.query(VitalSign).filter(
        VitalSign.user_id == current_user.id,
        VitalSign.recorded_at >= thirty_days_ago
    ).count()

    # Check for high-severity conditions
    critical_conditions = db.query(HealthCondition).filter(
        HealthCondition.user_id == current_user.id,
        HealthCondition.status == "active"
    ).count()

    if critical_conditions > 0:
        health_score -= 10

    # Generate risk alerts
    risk_alerts = []

    if recent_symptoms > 5:
        risk_alerts.append("Multiple symptoms reported this week - consider consulting a doctor")

    if recent_vitals == 0 and active_meds > 0:
        risk_alerts.append("No vital signs recorded recently - regular monitoring recommended")

    # Check for severe recent symptoms
    severe_symptoms = db.query(Symptom).filter(
        Symptom.user_id == current_user.id,
        Symptom.logged_at >= seven_days_ago,
        Symptom.severity.in_(["severe", "critical"])
    ).count()

    if severe_symptoms > 0:
        risk_alerts.append("Severe symptoms detected - immediate medical attention advised")
        health_score -= 15

    # Ensure health score is between 0 and 100
    health_score = max(0, min(100, health_score))

    return DashboardStats(
        health_score=round(health_score, 1),
        total_symptoms=recent_symptoms,
        active_medications=active_meds,
        recent_vitals_count=recent_vitals,
        pending_checkups=0,  # Could be calculated based on last checkup date
        risk_alerts=risk_alerts
    )


@router.get("/health-data", response_model=HealthDataResponse)
async def get_health_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all health data for the current user
    """
    # Get recent symptoms (last 90 days)
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    symptoms = db.query(Symptom).filter(
        Symptom.user_id == current_user.id,
        Symptom.logged_at >= ninety_days_ago
    ).order_by(Symptom.logged_at.desc()).all()

    # Get recent vital signs (last 90 days)
    vital_signs = db.query(VitalSign).filter(
        VitalSign.user_id == current_user.id,
        VitalSign.recorded_at >= ninety_days_ago
    ).order_by(VitalSign.recorded_at.desc()).all()

    # Get active medications
    medications = db.query(Medication).filter(
        Medication.user_id == current_user.id,
        Medication.is_active == 1
    ).order_by(Medication.created_at.desc()).all()

    # Get health conditions
    conditions = db.query(HealthCondition).filter(
        HealthCondition.user_id == current_user.id
    ).order_by(HealthCondition.created_at.desc()).all()

    # Get allergies
    allergies = db.query(Allergy).filter(
        Allergy.user_id == current_user.id
    ).order_by(Allergy.created_at.desc()).all()

    # Get recent reports (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    reports = db.query(MedicalReport).filter(
        MedicalReport.user_id == current_user.id,
        MedicalReport.uploaded_at >= six_months_ago
    ).order_by(MedicalReport.uploaded_at.desc()).all()

    return HealthDataResponse(
        symptoms=[SymptomResponse.from_orm(s) for s in symptoms],
        vital_signs=[VitalSignResponse.from_orm(v) for v in vital_signs],
        medications=[MedicationResponse.from_orm(m) for m in medications],
        conditions=[HealthConditionResponse.from_orm(c) for c in conditions],
        allergies=[AllergyResponse.from_orm(a) for a in allergies],
        recent_reports=[ReportResponse.from_orm(r) for r in reports]
    )


@router.get("/symptoms", response_model=List[SymptomResponse])
async def get_symptoms(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get symptoms for specified number of days
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    symptoms = db.query(Symptom).filter(
        Symptom.user_id == current_user.id,
        Symptom.logged_at >= start_date
    ).order_by(Symptom.logged_at.desc()).all()

    return [SymptomResponse.from_orm(s) for s in symptoms]


@router.get("/vitals", response_model=List[VitalSignResponse])
async def get_vitals(
    vital_type: str = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get vital signs for specified number of days and type
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    query = db.query(VitalSign).filter(
        VitalSign.user_id == current_user.id,
        VitalSign.recorded_at >= start_date
    )

    if vital_type:
        query = query.filter(VitalSign.type == vital_type)

    vitals = query.order_by(VitalSign.recorded_at.desc()).all()

    return [VitalSignResponse.from_orm(v) for v in vitals]


@router.get("/medications", response_model=List[MedicationResponse])
async def get_medications(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get medications (active or all)
    """
    query = db.query(Medication).filter(
        Medication.user_id == current_user.id
    )

    if active_only:
        query = query.filter(Medication.is_active == 1)

    medications = query.order_by(Medication.created_at.desc()).all()

    return [MedicationResponse.from_orm(m) for m in medications]


@router.get("/conditions", response_model=List[HealthConditionResponse])
async def get_conditions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all health conditions
    """
    conditions = db.query(HealthCondition).filter(
        HealthCondition.user_id == current_user.id
    ).order_by(HealthCondition.created_at.desc()).all()

    return [HealthConditionResponse.from_orm(c) for c in conditions]


@router.get("/allergies", response_model=List[AllergyResponse])
async def get_allergies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all allergies
    """
    allergies = db.query(Allergy).filter(
        Allergy.user_id == current_user.id
    ).order_by(Allergy.created_at.desc()).all()

    return [AllergyResponse.from_orm(a) for a in allergies]
