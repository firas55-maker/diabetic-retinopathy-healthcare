#!/usr/bin/env python3
"""
Test the image endpoint to see what error is being returned
"""

import sys
import requests

sys.path.insert(0, r'C:\Users\LENOVO\Desktop\helathcare 2\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Scan

# Create database connection
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

scan_id = "18077088-e841-4980-80bd-f202bfe80f67"

print(f"\n{'='*80}")
print(f"CHECKING SCAN IN DATABASE")
print(f"{'='*80}\n")

try:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()

    if not scan:
        print(f"❌ Scan NOT found in database")
        print(f"   Scan ID: {scan_id}")
    else:
        print(f"✅ Scan found in database")
        print(f"   Scan ID:     {scan.id}")
        print(f"   Patient:     {scan.patient.patient_code if scan.patient else 'N/A'}")
        print(f"   file_path:   {scan.file_path}")
        print(f"   Status:      {scan.status.value}")

        # Check file
        from pathlib import Path
        file_path = Path(scan.file_path)
        print(f"\n   Relative path exists: {file_path.exists()}")

        backend_dir = Path(__file__).parent.parent
        abs_path = backend_dir / file_path
        print(f"   Absolute path: {abs_path}")
        print(f"   Absolute exists: {abs_path.exists()}")

        if abs_path.exists():
            stat = abs_path.stat()
            print(f"   File size: {stat.st_size} bytes")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()

print(f"\n{'='*80}")
print(f"TESTING ENDPOINT")
print(f"{'='*80}\n")

# Try to call the endpoint without auth first to see if it exists
print(f"Testing: GET http://localhost:8000/doctor/scans/{scan_id}/image")
print(f"(without auth to see if endpoint exists)\n")

try:
    response = requests.get(
        f"http://localhost:8000/doctor/scans/{scan_id}/image",
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except requests.exceptions.ConnectionError:
    print(f"❌ Cannot connect to backend - is it running on localhost:8000?")
except Exception as e:
    print(f"Error: {e}")

print(f"\n{'='*80}\n")
