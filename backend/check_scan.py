#!/usr/bin/env python3
"""
Query the database to check scan file_path and verify file existence
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, r'C:\Users\LENOVO\Desktop\helathcare 2\backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Scan

# Create database connection
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Query the specific scan
scan_id = "5124fd0a-1c3e-4564-bd72-13d9661b82b2"
print(f"\n{'='*70}")
print(f"SCANNING DATABASE FOR: {scan_id}")
print(f"{'='*70}\n")

try:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()

    if not scan:
        print(f"❌ SCAN NOT FOUND in database")
        print(f"   Scan ID: {scan_id}")
        print(f"\n   The scan record does not exist in the database.")
        sys.exit(1)

    print(f"✅ SCAN FOUND in database")
    print(f"\n   Scan ID:      {scan.id}")
    print(f"   Patient ID:   {scan.patient_id}")
    print(f"   Patient Code: {scan.patient.patient_code if scan.patient else 'N/A'}")
    print(f"   AI Grade:     {scan.ai_grade}")
    print(f"   Status:       {scan.status.value}")
    print(f"   Created At:   {scan.created_at}")

    print(f"\n{'─'*70}")
    print(f"FILE PATH INFORMATION:")
    print(f"{'─'*70}\n")

    # Check file_path field
    file_path_value = scan.file_path
    print(f"   file_path column value:")
    print(f"   {file_path_value}\n")

    # Convert to Path object and check existence
    file_path = Path(file_path_value)
    print(f"   As Path object: {file_path}")
    print(f"   Absolute:       {file_path.absolute()}")
    print(f"   Exists:         {file_path.exists()}")

    if file_path.exists():
        print(f"\n✅ FILE EXISTS ON DISK")
        stat = file_path.stat()
        print(f"   Size:          {stat.st_size} bytes")
        print(f"   Modified:      {Path(file_path).stat()}")
    else:
        print(f"\n❌ FILE DOES NOT EXIST ON DISK")
        print(f"\n   The scan record exists in the database with file_path:")
        print(f"   {file_path_value}")
        print(f"\n   But the actual image file is missing from disk.")
        print(f"   This scan's image was never saved, or was deleted.")
        print(f"   You need to re-upload this scan to get a new image file.")

    print(f"\n{'='*70}\n")

except Exception as e:
    print(f"\n❌ ERROR querying database:")
    print(f"   {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    db.close()
