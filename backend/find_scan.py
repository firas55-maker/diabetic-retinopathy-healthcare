#!/usr/bin/env python3
"""
Find a valid scan to test the review endpoint
"""

import sys
import json

sys.path.insert(0, r'C:\Users\LENOVO\Desktop\helathcare 2\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import User, Scan, Patient, RoleEnum, ScanStatusEnum

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

    print(f"Doctor: {doctor.email}, Hospital: {doctor.hospital_id}")
    print()

    # Find ANY scan from this hospital
    scans = db.query(Scan).join(Patient).filter(
        Patient.hospital_id == doctor.hospital_id
    ).all()

    print(f"Total scans in doctor's hospital: {len(scans)}")

    if scans:
        for scan in scans[:3]:
            print(f"  - Scan {scan.id}: status={scan.status.value}, patient_id={scan.patient_id}")
    else:
        print("No scans found")

finally:
    db.close()
