from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from uuid import UUID

from models import Patient, Scan, User, ScanStatusEnum, RoleEnum
from dependencies import require_doctor, require_doctor_or_technical_staff, get_current_user
from database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Response Models
class AgeGroupStats(BaseModel):
    """Age group statistics"""
    group: str
    count: int
    percentage: float

class MonthlyScanCount(BaseModel):
    """Monthly scan count"""
    year: int
    month: int
    month_name: str
    count: int

class DashboardStats(BaseModel):
    """Complete dashboard statistics"""
    total_patients: int
    reviewed_scans_count: int
    affected_scans_count: int
    affected_percentage: float
    age_group_breakdown: List[AgeGroupStats]
    monthly_scan_counts: List[MonthlyScanCount]
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "total_patients": 150,
                "reviewed_scans_count": 200,
                "affected_scans_count": 95,
                "affected_percentage": 47.5,
                "age_group_breakdown": [
                    {"group": "<30", "count": 5, "percentage": 3.3},
                    {"group": "30-50", "count": 45, "percentage": 30.0},
                    {"group": "50-65", "count": 65, "percentage": 43.3},
                    {"group": "65+", "count": 35, "percentage": 23.3}
                ],
                "monthly_scan_counts": [
                    {"year": 2026, "month": 1, "month_name": "January", "count": 12},
                    {"year": 2026, "month": 2, "month_name": "February", "count": 15}
                ],
                "timestamp": "2026-09-16T11:49:27.449Z"
            }
        }

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

def calculate_age_from_dob(dob) -> int:
    """Calculate age from date of birth"""
    today = datetime.now(timezone.utc).date()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def get_age_group(age: int) -> str:
    """Categorize age into groups"""
    if age < 30:
        return "<30"
    elif age < 50:
        return "30-50"
    elif age < 65:
        return "50-65"
    else:
        return "65+"

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_technical_staff)
) -> DashboardStats:
    """
    Get comprehensive dashboard statistics (doctor or technical staff)

    Returns:
    - **total_patients**: Total number of patients in doctor's hospital
    - **reviewed_scans_count**: Total scans reviewed by doctor
    - **affected_scans_count**: Scans with doctor_grade >= 2 (Moderate or worse)
    - **affected_percentage**: Percentage of reviewed scans showing DR (grade >= 2)
    - **age_group_breakdown**: Affected patients grouped by age (<30, 30-50, 50-65, 65+)
    - **monthly_scan_counts**: Scan upload counts for last 12 months

    All statistics filtered by doctor's hospital
    """

    hospital_id = current_user.hospital_id

    # 1. Total patients in hospital
    total_patients = db.query(func.count(Patient.id)).filter(
        Patient.hospital_id == hospital_id
    ).scalar() or 0

    # 2. Reviewed scans and affected count
    reviewed_scans_query = db.query(Scan).filter(
        and_(
            Scan.status == ScanStatusEnum.REVIEWED,
            Scan.reviewed_by_id == current_user.id
        )
    )

    reviewed_scans_count = reviewed_scans_query.count()

    # Count affected scans (doctor_grade >= 2: Moderate, Severe, Proliferative)
    affected_scans_count = reviewed_scans_query.filter(
        Scan.doctor_grade >= 2
    ).count()

    # Calculate percentage
    affected_percentage = (
        (affected_scans_count / reviewed_scans_count * 100)
        if reviewed_scans_count > 0
        else 0.0
    )

    # 3. Age group breakdown for affected patients
    affected_patients = db.query(
        func.distinct(Scan.patient_id)
    ).join(
        Patient, Scan.patient_id == Patient.id
    ).filter(
        and_(
            Scan.reviewed_by_id == current_user.id,
            Scan.status == ScanStatusEnum.REVIEWED,
            Scan.doctor_grade >= 2
        )
    ).all()

    affected_patient_ids = [p[0] for p in affected_patients]

    age_group_stats = {}
    for group in ["<30", "30-50", "50-65", "65+"]:
        age_group_stats[group] = 0

    if affected_patient_ids:
        affected_patients_data = db.query(Patient).filter(
            Patient.id.in_(affected_patient_ids)
        ).all()

        # Calculate ages and group them
        for patient in affected_patients_data:
            age = calculate_age_from_dob(patient.date_of_birth)
            group = get_age_group(age)
            age_group_stats[group] += 1

    # Build age group breakdown with percentages
    total_affected = len(affected_patient_ids)
    age_group_breakdown = []

    for group in ["<30", "30-50", "50-65", "65+"]:
        count = age_group_stats[group]
        percentage = (count / total_affected * 100) if total_affected > 0 else 0.0
        age_group_breakdown.append(
            AgeGroupStats(group=group, count=count, percentage=round(percentage, 1))
        )

    # 4. Monthly scan counts for last 12 months
    now = datetime.now(timezone.utc)
    twelve_months_ago = now - timedelta(days=365)

    monthly_scans = db.query(
        extract("year", Scan.created_at).label("year"),
        extract("month", Scan.created_at).label("month"),
        func.count(Scan.id).label("count")
    ).filter(
        and_(
            Scan.created_at >= twelve_months_ago,
            Scan.patient.has(
                Patient.hospital_id == hospital_id
            )
        )
    ).group_by(
        extract("year", Scan.created_at),
        extract("month", Scan.created_at)
    ).order_by(
        extract("year", Scan.created_at),
        extract("month", Scan.created_at)
    ).all()

    # Build monthly data with all months (fill zeros for gaps)
    monthly_data_dict = {}
    for year, month, count in monthly_scans:
        key = (int(year), int(month))
        monthly_data_dict[key] = count

    # Generate list for last 12 months
    monthly_scan_counts = []
    for i in range(11, -1, -1):  # Last 12 months
        check_date = now - timedelta(days=30 * i)
        year = check_date.year
        month = check_date.month
        key = (year, month)

        count = monthly_data_dict.get(key, 0)
        monthly_scan_counts.append(
            MonthlyScanCount(
                year=year,
                month=month,
                month_name=MONTH_NAMES[month],
                count=count
            )
        )

    return DashboardStats(
        total_patients=total_patients,
        reviewed_scans_count=reviewed_scans_count,
        affected_scans_count=affected_scans_count,
        affected_percentage=round(affected_percentage, 1),
        age_group_breakdown=age_group_breakdown,
        monthly_scan_counts=monthly_scan_counts,
        timestamp=datetime.now(timezone.utc)
    )

@router.get("/stats/hospital", response_model=DashboardStats)
async def get_hospital_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
) -> DashboardStats:
    """
    Get hospital-wide dashboard statistics (all doctors' reviews)

    Same as /stats but aggregates across all doctors in the hospital.
    For comparing individual doctor performance to hospital averages.
    """

    hospital_id = current_user.hospital_id

    # 1. Total patients in hospital
    total_patients = db.query(func.count(Patient.id)).filter(
        Patient.hospital_id == hospital_id
    ).scalar() or 0

    # 2. All reviewed scans in hospital
    reviewed_scans_query = db.query(Scan).join(
        Patient, Scan.patient_id == Patient.id
    ).filter(
        and_(
            Scan.status == ScanStatusEnum.REVIEWED,
            Patient.hospital_id == hospital_id
        )
    )

    reviewed_scans_count = reviewed_scans_query.count()

    # Count affected scans (doctor_grade >= 2)
    affected_scans_count = reviewed_scans_query.filter(
        Scan.doctor_grade >= 2
    ).count()

    # Calculate percentage
    affected_percentage = (
        (affected_scans_count / reviewed_scans_count * 100)
        if reviewed_scans_count > 0
        else 0.0
    )

    # 3. Age group breakdown for affected patients
    affected_patients = db.query(
        func.distinct(Scan.patient_id)
    ).join(
        Patient, Scan.patient_id == Patient.id
    ).filter(
        and_(
            Patient.hospital_id == hospital_id,
            Scan.status == ScanStatusEnum.REVIEWED,
            Scan.doctor_grade >= 2
        )
    ).all()

    affected_patient_ids = [p[0] for p in affected_patients]

    age_group_stats = {}
    for group in ["<30", "30-50", "50-65", "65+"]:
        age_group_stats[group] = 0

    if affected_patient_ids:
        affected_patients_data = db.query(Patient).filter(
            Patient.id.in_(affected_patient_ids)
        ).all()

        for patient in affected_patients_data:
            age = calculate_age_from_dob(patient.date_of_birth)
            group = get_age_group(age)
            age_group_stats[group] += 1

    # Build age group breakdown
    total_affected = len(affected_patient_ids)
    age_group_breakdown = []

    for group in ["<30", "30-50", "50-65", "65+"]:
        count = age_group_stats[group]
        percentage = (count / total_affected * 100) if total_affected > 0 else 0.0
        age_group_breakdown.append(
            AgeGroupStats(group=group, count=count, percentage=round(percentage, 1))
        )

    # 4. Monthly scan counts for last 12 months
    now = datetime.now(timezone.utc)
    twelve_months_ago = now - timedelta(days=365)

    monthly_scans = db.query(
        extract("year", Scan.created_at).label("year"),
        extract("month", Scan.created_at).label("month"),
        func.count(Scan.id).label("count")
    ).join(
        Patient, Scan.patient_id == Patient.id
    ).filter(
        and_(
            Scan.created_at >= twelve_months_ago,
            Patient.hospital_id == hospital_id
        )
    ).group_by(
        extract("year", Scan.created_at),
        extract("month", Scan.created_at)
    ).order_by(
        extract("year", Scan.created_at),
        extract("month", Scan.created_at)
    ).all()

    # Build monthly data
    monthly_data_dict = {}
    for year, month, count in monthly_scans:
        key = (int(year), int(month))
        monthly_data_dict[key] = count

    # Generate list for last 12 months
    monthly_scan_counts = []
    for i in range(11, -1, -1):
        check_date = now - timedelta(days=30 * i)
        year = check_date.year
        month = check_date.month
        key = (year, month)

        count = monthly_data_dict.get(key, 0)
        monthly_scan_counts.append(
            MonthlyScanCount(
                year=year,
                month=month,
                month_name=MONTH_NAMES[month],
                count=count
            )
        )

    return DashboardStats(
        total_patients=total_patients,
        reviewed_scans_count=reviewed_scans_count,
        affected_scans_count=affected_scans_count,
        affected_percentage=round(affected_percentage, 1),
        age_group_breakdown=age_group_breakdown,
        monthly_scan_counts=monthly_scan_counts,
        timestamp=datetime.now(timezone.utc)
    )
