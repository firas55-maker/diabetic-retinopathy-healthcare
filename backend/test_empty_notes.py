#!/usr/bin/env python3
"""
Test the review endpoint with empty notes
"""

import sys
import requests
import json

sys.path.insert(0, r'C:\Users\LENOVO\Desktop\helathcare 2\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import User, Scan, Patient, RoleEnum, ScanStatusEnum
from jose import jwt

# Create database connection
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Find a doctor user
    doctor = db.query(User).filter(User.role == RoleEnum.DOCTOR).first()

    if not doctor:
        print("No doctor found")
        sys.exit(1)

    # Find a PENDING_REVIEW scan
    scan = db.query(Scan).join(Patient).filter(
        Patient.hospital_id == doctor.hospital_id,
        Scan.status == ScanStatusEnum.PENDING_REVIEW
    ).first()

    if not scan:
        print("No pending review scans found")
        sys.exit(1)

    print(f"Doctor: {doctor.email}")
    print(f"Scan ID: {scan.id}")
    print(f"Scan Status: {scan.status.value}")
    print()

    # Create JWT token
    token_data = {
        "email": doctor.email,
        "user_id": str(doctor.id),
        "role": doctor.role.value
    }

    token = jwt.encode(
        token_data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    print("=" * 80)
    print(f"Testing POST /doctor/scans/{scan.id}/review with EMPTY notes")
    print("=" * 80)
    print()

    # Test with empty notes
    review_data = {
        "doctor_grade": 2,
        "notes": ""
    }

    print(f"Request body:")
    print(json.dumps(review_data, indent=2))
    print()

    response = requests.post(
        f"http://localhost:8000/doctor/scans/{scan.id}/review",
        headers={"Authorization": f"Bearer {token}"},
        json=review_data,
        timeout=5
    )

    print(f"Status: {response.status_code}")
    print()
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

finally:
    db.close()
