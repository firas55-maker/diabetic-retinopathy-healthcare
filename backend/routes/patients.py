from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from datetime import datetime, date, timezone
from uuid import uuid4, UUID
import os
import shutil
from pathlib import Path
import base64
from typing import Optional, List
from pydantic import BaseModel

from models import Patient, Scan, User, ScanStatusEnum, RoleEnum
from schemas import (
    PatientCreateRequest,
    PatientCreateResponse,
    PatientResponse,
    ScanUploadResponse,
    ScanResponse,
    ScanListResponse
)
from dependencies import require_technical_staff, get_current_user
from database import get_db
from inference import predict

# Path to trained Siamese Network model weights
MODEL_PATH = Path(__file__).parent.parent / "ml_models" / "siamese_net_400x400_2.pt"

router = APIRouter(prefix="/patients", tags=["patients"])
scans_router = APIRouter(prefix="/scans", tags=["scans"])
lookup_router = APIRouter(prefix="/patient-lookup", tags=["patient-lookup"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("./uploads/scans")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def generate_patient_code(hospital_id: str, sequence: int) -> str:
    """Generate unique patient code"""
    # Format: PAT-YYYY-MM-DD-NNNN
    today = datetime.now().strftime("%Y%m%d")
    return f"PAT-{today}-{sequence:04d}"

@router.post("/", response_model=PatientCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    request: PatientCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technical_staff)
) -> PatientCreateResponse:
    """
    Register a new patient (technical_staff only)

    - **full_name**: Patient's full name
    - **date_of_birth**: Patient's date of birth (YYYY-MM-DD)
    - **sex**: Patient's sex (male, female, other)
    """

    try:
        # Parse date of birth
        dob = datetime.strptime(request.date_of_birth, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Validate sex
    valid_sexes = ["male", "female", "other"]
    if request.sex.lower() not in valid_sexes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sex. Must be one of: {', '.join(valid_sexes)}"
        )

    # Generate unique patient code
    # Get latest sequence number for today
    today = datetime.now().strftime("%Y%m%d")
    latest_patient = db.query(Patient).filter(
        Patient.patient_code.ilike(f"PAT-{today}-%")
    ).order_by(Patient.patient_code.desc()).first()

    if latest_patient:
        # Extract sequence number and increment
        seq = int(latest_patient.patient_code.split("-")[-1])
        new_seq = seq + 1
    else:
        new_seq = 1

    patient_code = generate_patient_code(str(current_user.hospital_id), new_seq)

    # Create patient
    new_patient = Patient(
        patient_code=patient_code,
        full_name=request.full_name,
        date_of_birth=dob,
        sex=request.sex.lower(),
        hospital_id=current_user.hospital_id
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return PatientCreateResponse(
        patient_code=new_patient.patient_code,
        id=new_patient.id,
        full_name=new_patient.full_name
    )

@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[PatientResponse]:
    """
    Get all patients from current user's hospital (paginated)

    Returns list of patients accessible to the authenticated user,
    filtered by their hospital. Supports pagination with skip/limit.

    - **skip**: Number of records to skip (default 0)
    - **limit**: Maximum records to return (default 50, max 200)
    """

    # Get all patients from the current user's hospital
    patients = db.query(Patient).filter(
        Patient.hospital_id == current_user.hospital_id
    ).order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()

    # Convert date_of_birth to string for response schema
    patient_responses = []
    for p in patients:
        patient_responses.append(PatientResponse(
            id=p.id,
            patient_code=p.patient_code,
            full_name=p.full_name,
            date_of_birth=str(p.date_of_birth),
            sex=p.sex,
            hospital_id=p.hospital_id,
            created_at=p.created_at,
            updated_at=p.updated_at
        ))

    return patient_responses

@router.get("/{patient_code}", response_model=PatientResponse)
async def get_patient(
    patient_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PatientResponse:
    """Get patient details by patient code"""

    patient = db.query(Patient).filter(
        Patient.patient_code == patient_code,
        Patient.hospital_id == current_user.hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with code {patient_code} not found"
        )

    return PatientResponse.model_validate(patient)

# Scan Routes

@scans_router.post("/", response_model=ScanUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_scan(
    patient_code: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technical_staff)
) -> ScanUploadResponse:
    """
    Upload retinal scan image for a patient (technical_staff only)

    - **patient_code**: Patient code (from registration)
    - **file**: Retinal fundus image (JPEG, PNG, WebP)

    Returns scan details with AI predictions
    """

    # Validate file type
    allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Find patient
    patient = db.query(Patient).filter(
        Patient.patient_code == patient_code,
        Patient.hospital_id == current_user.hospital_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with code {patient_code} not found in your hospital"
        )

    # Save uploaded file
    file_id = str(uuid4())
    file_path = UPLOAD_DIR / f"{file_id}.{file_ext}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Run inference on the uploaded image using real Siamese Network model
    try:
        prediction = predict(str(file_path), model_path=str(MODEL_PATH))
        ai_grade = prediction["grade"]
        ai_severity = prediction["severity"]
        ai_confidence = prediction["confidence"]
    except Exception as e:
        # Clean up file on prediction error
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze image: {str(e)}"
        )

    # Create scan record
    scan = Scan(
        patient_id=patient.id,
        uploaded_by_id=current_user.id,
        file_path=str(file_path),
        ai_grade=ai_grade,
        ai_confidence=ai_confidence,
        ai_severity=ai_severity,
        status=ScanStatusEnum.PENDING_REVIEW
    )

    db.add(scan)
    db.commit()
    db.refresh(scan)

    return ScanUploadResponse(
        scan_id=scan.id,
        patient_code=patient.patient_code,
        ai_grade=ai_grade,
        ai_severity=ai_severity,
        ai_confidence=ai_confidence,
        status=scan.status.value
    )

@scans_router.get("/mine", response_model=ScanListResponse)
async def get_my_scans(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technical_staff),
    skip: int = 0,
    limit: int = 50
) -> ScanListResponse:
    """
    Get all scans uploaded by the current technical staff member

    Returns scans with current status (pending_review, reviewed, archived)
    """

    # Query scans uploaded by this user
    scans = db.query(Scan).filter(
        Scan.uploaded_by_id == current_user.id
    ).order_by(Scan.created_at.desc()).offset(skip).limit(limit).all()

    total = db.query(Scan).filter(
        Scan.uploaded_by_id == current_user.id
    ).count()

    # Build response with nested patient data
    scan_responses = []
    for scan in scans:
        scan_resp = ScanResponse(
            id=scan.id,
            patient_code=scan.patient.patient_code,
            ai_grade=scan.ai_grade,
            ai_severity=scan.ai_severity,
            ai_confidence=scan.ai_confidence,
            status=scan.status.value,
            doctor_grade=scan.doctor_grade,
            doctor_notes=scan.doctor_notes,
            reviewed_at=scan.reviewed_at,
            created_at=scan.created_at,
            uploaded_by_email=scan.uploaded_by.email
        )
        scan_responses.append(scan_resp)

    return ScanListResponse(scans=scan_responses, total=total)

@scans_router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ScanResponse:
    """Get scan details by scan ID"""

    scan = db.query(Scan).filter(Scan.id == scan_id).first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan not found"
        )

    # Check authorization (uploader, doctor, or admin)
    is_uploader = scan.uploaded_by_id == current_user.id
    is_doctor = current_user.role == RoleEnum.DOCTOR
    is_admin = current_user.role == RoleEnum.ADMIN

    if not (is_uploader or is_doctor or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this scan"
        )

    return ScanResponse(
        id=scan.id,
        patient_code=scan.patient.patient_code,
        ai_grade=scan.ai_grade,
        ai_severity=scan.ai_severity,
        ai_confidence=scan.ai_confidence,
        status=scan.status.value,
        doctor_grade=scan.doctor_grade,
        doctor_notes=scan.doctor_notes,
        reviewed_at=scan.reviewed_at,
        created_at=scan.created_at,
        uploaded_by_email=scan.uploaded_by.email
    )

# Patient Lookup Routes (Public)

class PatientLookupScan(BaseModel):
    """Scan data visible to patient"""
    id: UUID
    date: datetime
    doctor_grade: Optional[int] = None
    doctor_notes: Optional[str] = None
    ai_grade: int
    ai_severity: str
    status: str
    image_path: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440004",
                "date": "2026-09-16T10:30:00",
                "doctor_grade": 2,
                "doctor_notes": "Confirmed moderate DR. Multiple microaneurysms visible. Recommend close follow-up.",
                "ai_grade": 2,
                "ai_severity": "Moderate",
                "status": "reviewed",
                "image_path": "/uploads/scans/550e8400-e29b-41d4-a716-446655440004.jpg"
            }
        }

class PatientLookupResponse(BaseModel):
    """Patient lookup response with scan history"""
    patient_code: str
    full_name: str
    date_of_birth: str
    sex: str
    total_scans: int
    scans: List[PatientLookupScan]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "patient_code": "PAT-20260916-0001",
                "full_name": "Jane Smith",
                "date_of_birth": "1990-05-15",
                "sex": "female",
                "total_scans": 3,
                "scans": []
            }
        }

@lookup_router.get("/{patient_code}", response_model=PatientLookupResponse, tags=["public"])
async def patient_lookup(
    patient_code: str,
    date_of_birth: str = Query(..., description="Patient's date of birth (YYYY-MM-DD) for verification"),
    db: Session = Depends(get_db)
) -> PatientLookupResponse:
    """
    Public patient lookup endpoint (no authentication required)

    Returns patient's own scan history with doctor assessments.
    Requires date_of_birth as a verification parameter to prevent data leakage.

    - **patient_code**: Patient's registration code (e.g., PAT-20260916-0001)
    - **date_of_birth**: Patient's date of birth (YYYY-MM-DD) - required for verification

    Returns:
    - Patient demographics
    - All scans with:
      - Date of scan
      - AI grade and severity
      - Doctor grade and clinical notes (if reviewed)
      - Current status
      - Image file path
    """

    # Parse and validate date of birth
    try:
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Find patient by patient_code
    patient = db.query(Patient).filter(
        Patient.patient_code == patient_code
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # Verify date of birth for security
    if patient.date_of_birth != dob:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Date of birth verification failed. Access denied."
        )

    # Get all scans for this patient
    scans = db.query(Scan).filter(
        Scan.patient_id == patient.id
    ).order_by(Scan.created_at.desc()).all()

    # Build scan responses - only include reviewed scans or all scans?
    # Returning all scans per request, but only including doctor_grade/notes if reviewed
    scan_responses = []
    for scan in scans:
        scan_resp = PatientLookupScan(
            id=scan.id,
            date=scan.created_at,
            doctor_grade=scan.doctor_grade if scan.status == ScanStatusEnum.REVIEWED else None,
            doctor_notes=scan.doctor_notes if scan.status == ScanStatusEnum.REVIEWED else None,
            ai_grade=scan.ai_grade,
            ai_severity=scan.ai_severity,
            status=scan.status.value,
            image_path=scan.file_path
        )
        scan_responses.append(scan_resp)

    return PatientLookupResponse(
        patient_code=patient.patient_code,
        full_name=patient.full_name,
        date_of_birth=str(patient.date_of_birth),
        sex=patient.sex,
        total_scans=len(scans),
        scans=scan_responses
    )
