#!/usr/bin/env python3
"""End-to-end test: simulate the bug scenario"""

import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from sqlalchemy import text
from database import SessionLocal, engine
from models import User, Hospital
from auth_utils import hash_password, verify_password
from datetime import datetime, timezone
import uuid

print("="*70)
print("STEP 1: Check if test hospital and user exist in DB")
print("="*70)

db = SessionLocal()

# First, ensure a test hospital exists
test_hospital_id = "00000000-0000-0000-0000-000000000001"
hospital = db.query(Hospital).filter(Hospital.id == test_hospital_id).first()

if not hospital:
    print("Creating test hospital...")
    hospital = Hospital(
        id=uuid.UUID(test_hospital_id),
        name="Test Hospital",
        region="Test Region",
        city="Test City"
    )
    db.add(hospital)
    db.commit()
    print(f"✓ Test hospital created: {hospital.id}")
else:
    print(f"✓ Test hospital already exists: {hospital.id}")

# Check if test user exists
test_email = "test_doctor@hospital.com"
existing_user = db.query(User).filter(User.email == test_email).first()

if existing_user:
    print(f"✓ Test user already exists: {existing_user.email}")
    db.delete(existing_user)
    db.commit()
    print(f"  (Deleted for clean test)")

print("\n" + "="*70)
print("STEP 2: Create test user with known password (simulating your script)")
print("="*70)

test_password = "testpass123"
hashed = hash_password(test_password)
print(f"Password: {test_password}")
print(f"Hash: {hashed[:30]}..." if len(hashed) > 30 else f"Hash: {hashed}")

new_user = User(
    id=uuid.uuid4(),
    email=test_email,
    hashed_password=hashed,
    full_name="Test Doctor",
    role="doctor",
    hospital_id=uuid.UUID(test_hospital_id),
    specialty="Ophthalmology"
)

db.add(new_user)
db.commit()
db.refresh(new_user)
print(f"✓ User created and committed to DB: {new_user.email}")

print("\n" + "="*70)
print("STEP 3: Query fresh from DB and verify password locally")
print("="*70)

# Create a NEW session (simulating a separate request)
db_fresh = SessionLocal()
user_from_db = db_fresh.query(User).filter(User.email == test_email).first()

if user_from_db:
    print(f"✓ User retrieved from DB: {user_from_db.email}")
    print(f"  Stored hash: {user_from_db.hashed_password[:30]}...")

    # Verify password locally (this is what login route does)
    verify_result = verify_password(test_password, user_from_db.hashed_password)
    print(f"\nverify_password('{test_password}', stored_hash) = {verify_result}")

    if verify_result:
        print("✓ PASSWORD VERIFICATION SUCCEEDED")
    else:
        print("✗ PASSWORD VERIFICATION FAILED - BUG CONFIRMED")
else:
    print("✗ User not found in fresh DB query!")

db_fresh.close()
db.close()

print("\n" + "="*70)
print("STEP 4: Now test via FastAPI /auth/login endpoint")
print("="*70)

# Import FastAPI test client
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

login_payload = {
    "email": test_email,
    "password": test_password
}

print(f"Sending POST /auth/login with:")
print(f"  email: {login_payload['email']}")
print(f"  password: {login_payload['password']}")

response = client.post("/auth/login", json=login_payload)

print(f"\nResponse status: {response.status_code}")
print(f"Response body: {response.json()}")

if response.status_code == 200:
    print("\n✓ LOGIN SUCCEEDED - Bug is FIXED")
    print(f"  Token: {response.json().get('access_token', 'N/A')[:30]}...")
else:
    print(f"\n✗ LOGIN FAILED with status {response.status_code}")
    print(f"  Message: {response.json().get('detail', 'Unknown error')}")

print("\n" + "="*70)
