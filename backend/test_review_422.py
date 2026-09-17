#!/usr/bin/env python3
"""
Test the review endpoint and capture the 422 error response
"""

import sys
import requests
import json

sys.path.insert(0, r'C:\Users\LENOVO\Desktop\helathcare 2\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import User, RoleEnum
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

    print(f"Doctor: {doctor.email}")
    print(f"Token: {token[:50]}...")
    print()

    # Use the scan ID from the frontend
    scan_id = "18077088-e841-4980-80bd-f202bfe80f67"

    print("=" * 80)
    print(f"Testing POST /doctor/scans/{scan_id}/review")
    print("=" * 80)
    print()

    # Test with the exact request body from frontend
    review_data = {
        "doctor_grade": 2,
        "notes": "Test clinical notes"
    }

    print(f"Request body:")
    print(json.dumps(review_data, indent=2))
    print()

    response = requests.post(
        f"http://localhost:8000/doctor/scans/{scan_id}/review",
        headers={"Authorization": f"Bearer {token}"},
        json=review_data,
        timeout=5
    )

    print(f"Status: {response.status_code}")
    print()
    print(f"Response headers:")
    for key, val in response.headers.items():
        print(f"  {key}: {val}")
    print()
    print(f"Response body:")
    print(response.text)

finally:
    db.close()
