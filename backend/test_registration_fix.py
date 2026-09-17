import requests
import json
from uuid import uuid4

BASE_URL = "http://127.0.0.1:8000"

# The hospital_id that does NOT exist
invalid_hospital_id = "550e8400-e29b-41d4-a716-446655440000"

# The hospital_id that DOES exist
valid_hospital_id = "86aabaf3-0d6b-436d-880f-52478a0e92e2"

print("=" * 60)
print("TEST 1: Register with NON-EXISTENT hospital_id")
print("=" * 60)

test1_email = f"test.invalid.hospital.{uuid4().hex[:8]}@hospital.com"
test1_payload = {
    "email": test1_email,
    "password": "securepassword123",
    "full_name": "Test User Invalid Hospital",
    "role": "doctor",
    "hospital_id": invalid_hospital_id,
    "specialty": "Testing"
}

print(f"\nPOST /auth/register")
print(f"Payload: {json.dumps(test1_payload, indent=2)}")

try:
    response = requests.post(f"{BASE_URL}/auth/register", json=test1_payload, timeout=5)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("TEST 2: Register with VALID hospital_id")
print("=" * 60)

test2_email = f"test.valid.hospital.{uuid4().hex[:8]}@hospital.com"
test2_payload = {
    "email": test2_email,
    "password": "securepassword123",
    "full_name": "Test User Valid Hospital",
    "role": "doctor",
    "hospital_id": valid_hospital_id,
    "specialty": "Cardiology"
}

print(f"\nPOST /auth/register")
print(f"Payload: {json.dumps(test2_payload, indent=2)}")

try:
    response = requests.post(f"{BASE_URL}/auth/register", json=test2_payload, timeout=5)
    print(f"\nStatus: {response.status_code}")
    response_data = response.json()
    print(f"Response keys: {list(response_data.keys())}")
    if "access_token" in response_data:
        print(f"✓ access_token present (length: {len(response_data['access_token'])})")
    if "token_type" in response_data:
        print(f"✓ token_type: {response_data['token_type']}")
    if "expires_in" in response_data:
        print(f"✓ expires_in: {response_data['expires_in']}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("TEST 3: Verify user was persisted in database")
print("=" * 60)

from database import SessionLocal
from models import User

db = SessionLocal()
user = db.query(User).filter(User.email == test2_email).first()
if user:
    print(f"✓ User found in database")
    print(f"  Email: {user.email}")
    print(f"  Full Name: {user.full_name}")
    print(f"  Hospital ID: {user.hospital_id}")
    print(f"  Role: {user.role.value}")
else:
    print(f"✗ User NOT found in database")

db.close()
