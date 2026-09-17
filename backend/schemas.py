from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

# Auth Schemas
class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72, description="Password must be 8-72 characters (bcrypt limit)")
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., description="doctor or technical_staff")
    hospital_id: UUID
    specialty: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "doctor@hospital.com",
                "password": "securepassword123",
                "full_name": "Dr. John Doe",
                "role": "doctor",
                "hospital_id": "550e8400-e29b-41d4-a716-446655440000",
                "specialty": "Ophthalmology"
            }
        }

class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "doctor@hospital.com",
                "password": "securepassword123"
            }
        }

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }

# User Schemas
class UserResponse(BaseModel):
    """User response model"""
    id: UUID
    email: str
    full_name: str
    role: str
    hospital_id: UUID
    specialty: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "doctor@hospital.com",
                "full_name": "Dr. John Doe",
                "role": "doctor",
                "hospital_id": "550e8400-e29b-41d4-a716-446655440001",
                "specialty": "Ophthalmology",
                "created_at": "2026-09-16T10:00:00",
                "updated_at": "2026-09-16T10:00:00"
            }
        }

# Hospital Schemas
class HospitalResponse(BaseModel):
    """Hospital response model"""
    id: UUID
    name: str
    region: str
    city: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Patient Schemas
class PatientCreateRequest(BaseModel):
    """Create patient request"""
    full_name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: str = Field(..., description="Date in format YYYY-MM-DD")
    sex: str = Field(..., description="male, female, or other")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Jane Smith",
                "date_of_birth": "1990-05-15",
                "sex": "female"
            }
        }

class PatientResponse(BaseModel):
    """Patient response model"""
    id: UUID
    patient_code: str
    full_name: str
    date_of_birth: str
    sex: str
    hospital_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "patient_code": "PAT-2026-001",
                "full_name": "Jane Smith",
                "date_of_birth": "1990-05-15",
                "sex": "female",
                "hospital_id": "550e8400-e29b-41d4-a716-446655440001",
                "created_at": "2026-09-16T10:00:00",
                "updated_at": "2026-09-16T10:00:00"
            }
        }

class PatientCreateResponse(BaseModel):
    """Response after creating patient"""
    patient_code: str
    id: UUID
    full_name: str

    class Config:
        from_attributes = True

# Scan Schemas
class ScanUploadResponse(BaseModel):
    """Scan upload response"""
    scan_id: UUID
    patient_code: str
    ai_grade: int
    ai_severity: str
    ai_confidence: float
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "scan_id": "550e8400-e29b-41d4-a716-446655440002",
                "patient_code": "PAT-2026-001",
                "ai_grade": 2,
                "ai_severity": "Moderate",
                "ai_confidence": 0.8765,
                "status": "pending_review"
            }
        }

class ScanResponse(BaseModel):
    """Scan details response"""
    id: UUID
    patient_code: str
    ai_grade: int
    ai_severity: str
    ai_confidence: float
    status: str
    doctor_grade: Optional[int] = None
    doctor_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    uploaded_by_email: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "patient_code": "PAT-2026-001",
                "ai_grade": 2,
                "ai_severity": "Moderate",
                "ai_confidence": 0.8765,
                "status": "pending_review",
                "doctor_grade": None,
                "doctor_notes": None,
                "reviewed_at": None,
                "created_at": "2026-09-16T10:00:00",
                "uploaded_by_email": "staff@hospital.com"
            }
        }

class ScanListResponse(BaseModel):
    """List of scans"""
    scans: List[ScanResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "scans": [],
                "total": 0
            }
        }

class ScanQueueResponse(BaseModel):
    """Scan in review queue"""
    id: UUID
    patient_code: str
    patient_name: str
    hospital_name: str
    region: str
    ai_grade: int
    ai_severity: str
    ai_confidence: float
    uploaded_at: datetime
    uploaded_by_email: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440004",
                "patient_code": "PAT-20260916-0001",
                "patient_name": "Jane Smith",
                "hospital_name": "Central Medical Hospital",
                "region": "North Region",
                "ai_grade": 2,
                "ai_severity": "Moderate",
                "ai_confidence": 0.8765,
                "uploaded_at": "2026-09-16T10:30:00",
                "uploaded_by_email": "staff@hospital.com"
            }
        }

class ScanQueueListResponse(BaseModel):
    """List of scans in review queue"""
    scans: List[ScanQueueResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "scans": [],
                "total": 0
            }
        }

class ScanDetailResponse(BaseModel):
    """Detailed scan information"""
    id: UUID
    patient_code: str
    patient_name: str
    patient_dob: str
    patient_sex: str
    hospital_name: str
    region: str
    city: str
    file_path: str
    image_data: Optional[str] = None
    ai_grade: int
    ai_severity: str
    ai_confidence: float
    status: str
    doctor_grade: Optional[int] = None
    doctor_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    uploaded_by_email: str
    uploaded_by_name: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440004",
                "patient_code": "PAT-20260916-0001",
                "patient_name": "Jane Smith",
                "patient_dob": "1990-05-15",
                "patient_sex": "female",
                "hospital_name": "Central Medical Hospital",
                "region": "North Region",
                "city": "New York",
                "file_path": "/uploads/scans/550e8400-e29b-41d4-a716-446655440004.jpg",
                "image_data": "base64_encoded_image_string_here",
                "ai_grade": 2,
                "ai_severity": "Moderate",
                "ai_confidence": 0.8765,
                "status": "pending_review",
                "doctor_grade": None,
                "doctor_notes": None,
                "reviewed_at": None,
                "created_at": "2026-09-16T10:30:00",
                "uploaded_by_email": "staff@hospital.com",
                "uploaded_by_name": "John Smith"
            }
        }

class ScanReviewRequest(BaseModel):
    """Doctor's scan review submission"""
    doctor_grade: int = Field(..., ge=0, le=4, description="0-4: No DR to Proliferative DR")
    notes: str = Field(default="", max_length=1000, description="Optional clinical notes")

    class Config:
        json_schema_extra = {
            "example": {
                "doctor_grade": 2,
                "notes": "Confirmed moderate DR. Multiple microaneurysms and venous abnormalities visible. Recommend close follow-up in 3 months."
            }
        }

class ScanReviewResponse(BaseModel):
    """Response after submitting review"""
    id: UUID
    patient_code: str
    status: str
    doctor_grade: int
    doctor_notes: str
    reviewed_at: datetime

    class Config:
        from_attributes = True

class PatientWithScansResponse(BaseModel):
    """Patient with scan history"""
    id: UUID
    patient_code: str
    full_name: str
    date_of_birth: str
    sex: str
    hospital_id: UUID
    scan_count: int
    latest_scan_date: Optional[datetime] = None
    latest_ai_grade: Optional[int] = None
    latest_doctor_grade: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "patient_code": "PAT-20260916-0001",
                "full_name": "Jane Smith",
                "date_of_birth": "1990-05-15",
                "sex": "female",
                "hospital_id": "550e8400-e29b-41d4-a716-446655440001",
                "scan_count": 3,
                "latest_scan_date": "2026-09-16T10:30:00",
                "latest_ai_grade": 2,
                "latest_doctor_grade": 2,
                "created_at": "2026-09-16T10:00:00"
            }
        }

class DoctorPatientsResponse(BaseModel):
    """List of patients reviewed by doctor"""
    patients: List[PatientWithScansResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "patients": [],
                "total": 0
            }
        }

# Error Response
class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    status_code: int
