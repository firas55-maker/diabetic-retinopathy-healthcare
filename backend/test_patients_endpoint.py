#!/usr/bin/env python3
"""
Test the /patients endpoint to capture the 500 error traceback
"""

import sys
import requests

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
        print("No doctor found in database")
        sys.exit(1)

    print(f"Found doctor: {doctor.email}")

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
    print("Testing GET /patients/?skip=0&limit=50")
    print("=" * 80)
    print()

    # Test the endpoint
    response = requests.get(
        "http://localhost:8000/patients/?skip=0&limit=50",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )

    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(response.text)

finally:
    db.close()
