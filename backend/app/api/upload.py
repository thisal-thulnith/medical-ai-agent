"""
File upload API for medical reports and images
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
from datetime import date
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.health_data import MedicalReport, ReportType
from app.schemas.health import ReportResponse
from app.services.file_processor import FileProcessorService

router = APIRouter(prefix="/upload", tags=["File Upload"])

# Create uploads directory
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

file_processor = FileProcessorService()


@router.post("/report", response_model=ReportResponse)
async def upload_medical_report(
    file: UploadFile = File(...),
    report_type: str = Form(...),
    report_date: Optional[str] = Form(None),
    conversation_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a medical report (PDF, image, etc.)
    AI will analyze and extract key information
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tif', '.tiff']
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
        )

    # Create user directory
    user_dir = UPLOAD_DIR / str(current_user.id)
    user_dir.mkdir(exist_ok=True)

    # Save file
    file_path = user_dir / file.filename
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Process file (OCR, extract text)
    try:
        parsed_data = await file_processor.process_medical_document(
            file_path=str(file_path),
            file_type=file_ext
        )

        # Extract structured data from the report
        if parsed_data.get("text"):
            structured_extraction = await file_processor.extract_structured_data(
                report_text=parsed_data["text"],
                report_type=report_type
            )
            parsed_data["structured_data"] = structured_extraction.get("structured_data")

        # Generate AI analysis
        ai_analysis = await file_processor.analyze_report(
            parsed_data=parsed_data,
            report_type=report_type,
            user_context={
                "conditions": [c.condition_name for c in current_user.health_conditions],
                "medications": [m.name for m in current_user.medications if m.is_active]
            }
        )

        # Compare with normal ranges if blood test
        if report_type == "blood_test" and parsed_data.get("structured_data"):
            try:
                test_results = parsed_data["structured_data"]
                if isinstance(test_results, dict):
                    range_comparison = await file_processor.compare_with_normal_ranges(test_results)
                    ai_analysis["range_comparison"] = range_comparison
            except Exception as e:
                print(f"Error comparing ranges: {e}")

    except Exception as e:
        parsed_data = {"error": str(e)}
        ai_analysis = {"error": "Could not process file"}

    # Save to database
    report = MedicalReport(
        user_id=current_user.id,
        conversation_id=conversation_id,
        report_type=ReportType(report_type),
        file_url=str(file_path),
        file_name=file.filename,
        parsed_data=parsed_data,
        ai_analysis=ai_analysis,
        report_date=date.fromisoformat(report_date) if report_date else None
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportResponse.from_orm(report)


@router.post("/image")
async def upload_symptom_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Upload image of symptom (rash, wound, etc.)
    """
    # Validate image type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.heic']
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Image type not supported. Allowed: {', '.join(allowed_extensions)}"
        )

    # Create user directory
    user_dir = UPLOAD_DIR / str(current_user.id) / "symptoms"
    user_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = user_dir / file.filename
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {
        "success": True,
        "file_url": str(file_path),
        "message": "Image uploaded successfully"
    }


@router.get("/reports", response_model=list[ReportResponse])
async def get_user_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all medical reports for the current user
    """
    reports = db.query(MedicalReport).filter(
        MedicalReport.user_id == current_user.id
    ).order_by(MedicalReport.uploaded_at.desc()).all()

    return [ReportResponse.from_orm(r) for r in reports]


@router.get("/reports/{report_id}/analysis")
async def get_report_longitudinal_analysis(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive longitudinal analysis for a report
    Analyzes trends across all user's medical history
    """
    # Get the specific report
    report = db.query(MedicalReport).filter(
        MedicalReport.id == report_id,
        MedicalReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Get all user's reports for comparison
    all_reports = db.query(MedicalReport).filter(
        MedicalReport.user_id == current_user.id
    ).order_by(MedicalReport.report_date).all()

    # Convert to serializable format
    report_history = []
    for r in all_reports:
        report_history.append({
            "id": r.id,
            "report_type": r.report_type.value,
            "report_date": r.report_date.isoformat() if r.report_date else None,
            "ai_analysis": r.ai_analysis,
            "parsed_data": r.parsed_data
        })

    # Generate longitudinal analysis
    longitudinal_analysis = await file_processor.generate_report_summary(
        report_id=report_id,
        user_reports=report_history
    )

    return {
        "report_id": report_id,
        "report_type": report.report_type.value,
        "longitudinal_analysis": longitudinal_analysis,
        "total_reports": len(all_reports),
        "report_date": report.report_date.isoformat() if report.report_date else None
    }


@router.get("/reports/summary/all")
async def get_all_reports_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a comprehensive summary of all medical reports
    Useful for dashboard and health overview
    """
    reports = db.query(MedicalReport).filter(
        MedicalReport.user_id == current_user.id
    ).order_by(MedicalReport.report_date.desc()).all()

    if not reports:
        return {
            "total_reports": 0,
            "report_types": {},
            "recent_findings": [],
            "message": "No reports uploaded yet"
        }

    # Group reports by type
    report_types = {}
    for report in reports:
        report_type = report.report_type.value
        if report_type not in report_types:
            report_types[report_type] = 0
        report_types[report_type] += 1

    # Get recent key findings from AI analysis
    recent_findings = []
    for report in reports[:5]:  # Last 5 reports
        if report.ai_analysis and "summary" in report.ai_analysis:
            recent_findings.append({
                "date": report.report_date.isoformat() if report.report_date else None,
                "type": report.report_type.value,
                "summary": report.ai_analysis["summary"][:200] + "..." if len(report.ai_analysis["summary"]) > 200 else report.ai_analysis["summary"]
            })

    return {
        "total_reports": len(reports),
        "report_types": report_types,
        "recent_findings": recent_findings,
        "oldest_report": reports[-1].report_date.isoformat() if reports[-1].report_date else None,
        "newest_report": reports[0].report_date.isoformat() if reports[0].report_date else None
    }
