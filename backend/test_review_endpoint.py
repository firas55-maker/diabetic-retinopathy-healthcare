#!/usr/bin/env python3
"""
Test the /doctor/scans/{scan_id}/review endpoint to capture the 422 error
"""

import sys
import requests
import json

sys.path.insert(0, r'C:\Users\LENOVO\Desktop\helathcare 2\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import User, Scan, RoleEnum
from jose import jwt

# Create database connection
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Find a doctor user
    doctor = db.query(User).filter(User.role == RoleEnum.DOCTOR).first()

    if not doctor:
        print("No doctor found in database")
        sys.exit(1)

    print(f"Found doctor: {doctor.email}")

    # Find a scan from their hospital that's pending_review
    scan = db.query(Scan).join(
        User, Scan.patient_id == User.id
    ).filter(
        Scan.patient.has(hospital_id=doctor.hospital_id)
    ).first()

    if not scan:
        print(f"No scans found for hospital {doctor.hospital_id}")
        sys.exit(1)

    print(f"Found scan: {scan.id}")
    print(f"Scan status: {scan.status.value}")

    # Create a JWT token for this doctor
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

    print(f"Created token: {token[:50]}...")
    print()
    print("=" * 80)
    print(f"Testing POST /doctor/scans/{scan.id}/review")
    print("=" * 80)
    print()

    # Test the endpoint with review data
    review_data = {
        "doctor_grade": 2,
        "notes": "Test clinical notes"
    }

    print(f"Request body: {json.dumps(review_data, indent=2)}")
    print()

    response = requests.post(
        f"http://localhost:8000/doctor/scans/{scan.id}/review",
        headers={"Authorization": f"Bearer {token}"},
        json=review_data,
        timeout=5
    )

    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

finally:
    db.close()
