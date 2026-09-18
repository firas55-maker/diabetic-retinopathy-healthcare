from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timezone
from pathlib import Path
import base64
import os

from models import Patient, Scan, User, ScanStatusEnum, RoleEnum
from schemas import (
    ScanQueueResponse,
    ScanQueueListResponse,
    ScanDetailResponse,
    ScanReviewRequest,
    ScanReviewResponse,
    PatientWithScansResponse,
    DoctorPatientsResponse
)
from dependencies import require_doctor, require_doctor_or_technical_staff, get_current_user
from database import get_db

router = APIRouter(prefix="/doctor", tags=["doctor"])

# Constants for severity mapping
SEVERITY_GRADES = {
    0: "No DR",
    1: "Mild",
    2: "Moderate",
    3: "Severe",
    4: "Proliferative DR"
}

def read_image_as_base64(file_path: str) -> str:
    """Read image file and encode as base64"""
    try:
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading image: {e}")
        return None

@router.get("/scans/queue", response_model=ScanQueueListResponse)
async def get_scan_queue(
    hospital_id: str = Query(None, description="Filter by hospital ID"),
    region: str = Query(None, description="Filter by region"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_technical_staff)
) -> ScanQueueListResponse:
    """
    Get all pending_review scans in queue (doctor only)

    Optionally filter by:
    - **hospital_id**: UUID of specific hospital
    - **region**: Region name (e.g., "North Region")

    Returns paginated list of scans awaiting review
    """

    # Base query: all pending_review scans from user's hospital
    query = db.query(Scan).join(Patient).join(Scan.uploaded_by).filter(
        and_(
            Scan.status == ScanStatusEnum.PENDING_REVIEW,
            Patient.hospital_id == current_user.hospital_id
        )
    )

    # Apply optional filters
    if hospital_id:
        query = query.filter(Patient.hospital_id == hospital_id)

    if region:
        from models import Hospital as HospitalModel
        query = query.join(HospitalModel, Patient.hospital_id == HospitalModel.id).filter(
            HospitalModel.region == region
        )

    # Get total count
    total = query.count()

    # Get paginated results
    scans = query.order_by(Scan.created_at.asc()).offset(skip).limit(limit).all()

    # Build response
    queue_items = []
    for scan in scans:
        item = ScanQueueResponse(
            id=scan.id,
            patient_code=scan.patient.patient_code,
            patient_name=scan.patient.full_name,
            hospital_name=scan.patient.hospital.name,
            region=scan.patient.hospital.region,
            ai_grade=scan.ai_grade,
            ai_severity=scan.ai_severity,
            ai_confidence=scan.ai_confidence,
            uploaded_at=scan.created_at,
            uploaded_by_email=scan.uploaded_by.email
        )
        queue_items.append(item)

    return ScanQueueListResponse(scans=queue_items, total=total)

@router.get("/scans/{scan_id}/image")
async def get_scan_image(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """
    Get scan image file (doctor only)

    Returns the actual image file for direct display in the browser.
    Authorization: doctor from same hospital or admin.
    """

    scan = db.query(Scan).filter(Scan.id == scan_id).first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )

    # Check authorization: doctor from same hospital or admin
    if current_user.role != RoleEnum.ADMIN and scan.patient.hospital_id != current_user.hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view scans from your hospital"
        )

    # Resolve file path: handle both relative and absolute paths
    # file_path from DB might be relative (e.g., "uploads/scans/uuid.jpg")
    # Convert to absolute path if it's relative
    file_path = Path(scan.file_path)
    if not file_path.is_absolute():
        # Resolve relative to the backend directory
        backend_dir = Path(__file__).parent.parent
        file_path = backend_dir / file_path

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on disk"
        )

    # Determine media type from file extension
    suffix = file_path.suffix.lower()
    media_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp'
    }
    media_type = media_type_map.get(suffix, 'image/jpeg')

    # DEBUG: Print the exact path being opened
    print(f"\n{'='*80}")
    print(f"[SCAN IMAGE ENDPOINT] Serving image for scan_id: {scan_id}")
    print(f"  DB file_path value: {scan.file_path}")
    print(f"  Resolved absolute:  {file_path}")
    print(f"  File exists:        {file_path.exists()}")
    print(f"  File size:          {file_path.stat().st_size if file_path.exists() else 'N/A'} bytes")
    print(f"  Content-Type:       {media_type}")
    print(f"{'='*80}\n")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=f"scan_{scan_id}{suffix}"
    )

@router.get("/scans/{scan_id}", response_model=ScanDetailResponse)
async def get_scan_detail(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
) -> ScanDetailResponse:
    """
    Get full scan details including image and metadata (doctor only)

    Returns:
    - Complete patient information
    - Scan image as base64-encoded data
    - AI predictions and confidence
    - Doctor review info (if already reviewed)
    """

    scan = db.query(Scan).filter(Scan.id == scan_id).first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )

    # Check authorization: doctor from same hospital or admin
    if current_user.role != RoleEnum.ADMIN and scan.patient.hospital_id != current_user.hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view scans from your hospital"
        )

    # Read image file as base64
    image_data = read_image_as_base64(scan.file_path)

    return ScanDetailResponse(
        id=scan.id,
        patient_code=scan.patient.patient_code,
        patient_name=scan.patient.full_name,
        patient_dob=str(scan.patient.date_of_birth),
        patient_sex=scan.patient.sex,
        hospital_name=scan.patient.hospital.name,
        region=scan.patient.hospital.region,
        city=scan.patient.hospital.city,
        file_path=scan.file_path,
        image_data=image_data,
        ai_grade=scan.ai_grade,
        ai_severity=scan.ai_severity,
        ai_confidence=scan.ai_confidence,
        status=scan.status.value,
        doctor_grade=scan.doctor_grade,
        doctor_notes=scan.doctor_notes,
        reviewed_at=scan.reviewed_at,
        created_at=scan.created_at,
        uploaded_by_email=scan.uploaded_by.email,
        uploaded_by_name=scan.uploaded_by.full_name
    )

@router.post("/scans/{scan_id}/review", response_model=ScanReviewResponse, status_code=status.HTTP_200_OK)
async def submit_scan_review(
    scan_id: str,
    review: ScanReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
) -> ScanReviewResponse:
    """
    Submit doctor review for a scan (doctor only)

    - **doctor_grade**: 0-4 severity grade (0=No DR, 4=Proliferative DR)
    - **notes**: Clinical notes and observations

    Updates scan status to 'reviewed' and records doctor's assessment
    """

    scan = db.query(Scan).filter(Scan.id == scan_id).first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )

    # Check authorization
    if current_user.role != RoleEnum.ADMIN and scan.patient.hospital_id != current_user.hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review scans from your hospital"
        )

    # Check if already reviewed
    if scan.status == ScanStatusEnum.REVIEWED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This scan has already been reviewed"
        )

    # Validate doctor_grade
    if review.doctor_grade not in range(0, 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor grade must be between 0 and 4"
        )

    # Update scan with review
    scan.doctor_grade = review.doctor_grade
    scan.doctor_notes = review.notes
    scan.status = ScanStatusEnum.REVIEWED
    scan.reviewed_by_id = current_user.id
    scan.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(scan)

    return ScanReviewResponse(
        id=scan.id,
        patient_code=scan.patient.patient_code,
        status=scan.status.value,
        doctor_grade=scan.doctor_grade,
        doctor_notes=scan.doctor_notes,
        reviewed_at=scan.reviewed_at
    )

@router.get("/patients/mine", response_model=DoctorPatientsResponse)
async def get_my_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_technical_staff)
) -> DoctorPatientsResponse:
    """
    Get all patients this doctor has reviewed scans for (doctor only)

    Returns patients with:
    - Scan count
    - Latest scan date
    - Latest AI grade and doctor grade
    - Full patient information
    """

    # Get distinct patients reviewed by this doctor
    reviewed_patients = db.query(Patient).join(
        Scan, Patient.id == Scan.patient_id
    ).filter(
        and_(
            Scan.reviewed_by_id == current_user.id,
            Patient.hospital_id == current_user.hospital_id
        )
    ).distinct().order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()

    # Get total count
    total = db.query(func.count(func.distinct(Patient.id))).join(
        Scan, Patient.id == Scan.patient_id
    ).filter(
        and_(
            Scan.reviewed_by_id == current_user.id,
            Patient.hospital_id == current_user.hospital_id
        )
    ).scalar()

    # Build response with scan statistics
    patient_responses = []
    for patient in reviewed_patients:
        # Get scan statistics
        scans = db.query(Scan).filter(
            and_(
                Scan.patient_id == patient.id,
                Scan.reviewed_by_id == current_user.id
            )
        ).order_by(Scan.created_at.desc()).all()

        latest_scan = scans[0] if scans else None

        patient_resp = PatientWithScansResponse(
            id=patient.id,
            patient_code=patient.patient_code,
            full_name=patient.full_name,
            date_of_birth=str(patient.date_of_birth),
            sex=patient.sex,
            hospital_id=patient.hospital_id,
            scan_count=len(scans),
            latest_scan_date=latest_scan.created_at if latest_scan else None,
            latest_ai_grade=latest_scan.ai_grade if latest_scan else None,
            latest_doctor_grade=latest_scan.doctor_grade if latest_scan else None,
            created_at=patient.created_at
        )
        patient_responses.append(patient_resp)

    return DoctorPatientsResponse(patients=patient_responses, total=total)

