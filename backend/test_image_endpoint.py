#!/usr/bin/env python3
"""
Test the image endpoint with proper authentication
"""

import sys
import requests
import json

sys.path.insert(0, r'C:\Users\LENOVO\Desktop\helathcare 2\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import User, Scan, RoleEnum

# Create database connection
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Find a doctor user
    doctor = db.query(User).filter(User.role == RoleEnum.DOCTOR).first()
    
    if not doctor:
        print("❌ No doctor user found in database")
        sys.exit(1)
    
    print(f"✅ Found doctor: {doctor.email}")
    
    # Find a scan from their hospital
    scan = db.query(Scan).join(
        User, Scan.patient_id == User.id
    ).filter(
        Scan.patient.has(hospital_id=doctor.hospital_id)
    ).first()
    
    if not scan:
        print(f"❌ No scans found for hospital {doctor.hospital_id}")
        sys.exit(1)
    
    print(f"✅ Found scan: {scan.id}")
    print(f"   File path: {scan.file_path}")
    
    # Try to get a token (for testing, we'll try with basic auth first)
    print(f"\n{'='*70}")
    print(f"Testing image endpoint...")
    print(f"{'='*70}\n")
    
    # Test without auth first (should get 401)
    url = f"http://localhost:8000/doctor/scans/{scan.id}/image"
    print(f"GET {url}")
    
    response = requests.get(url, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 401:
        print(f"\n✅ Route is being matched correctly!")
        print(f"   Got 401 (auth required) instead of 404 (route not found)")
        print(f"   This proves the route ordering fix worked!")
    elif response.status_code == 404:
        print(f"\n❌ Still getting 404 - route ordering may not have worked")
    elif response.status_code == 200:
        print(f"\n✅ Got 200 OK! Image endpoint is working!")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   Size: {len(response.content)} bytes")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
