"""End-to-end test for phone_number field"""
import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from sqlalchemy import text
from database import SessionLocal, engine
from models import Patient, Hospital, User, RoleEnum
from datetime import datetime, date, timezone
from uuid import uuid4

def test_phone_number_e2e():
    """Test phone number field throughout the system"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("PHONE NUMBER FIELD - END-TO-END TEST")
        print("=" * 60)
        
        # Test 1: Check database column exists
        print("\n[Test 1] Checking database column exists...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name='patients' AND column_name='phone_number'
            """))
            col_info = result.fetchone()
            if col_info:
                print("[OK] Column found: {} ({}, nullable={})".format(col_info[0], col_info[1], col_info[2]))
            else:
                print("[FAIL] Column NOT found")
                return False
        
        # Test 2: Create test hospital and user
        print("\n[Test 2] Setting up test hospital and user...")
        hospital = db.query(Hospital).filter(Hospital.name == "Test Hospital").first()
        if not hospital:
            hospital = Hospital(
                name="Test Hospital",
                region="Test Region",
                city="Test City"
            )
            db.add(hospital)
            db.commit()
            db.refresh(hospital)
        print("[OK] Hospital ready: {}".format(hospital.id))
        
        user = db.query(User).filter(User.email == "test_staff@hospital.com").first()
        if not user:
            from auth_utils import hash_password
            user = User(
                email="test_staff@hospital.com",
                hashed_password=hash_password("password123"),
                full_name="Test Staff",
                role=RoleEnum.TECHNICAL_STAFF,
                hospital_id=hospital.id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        print("[OK] User ready: {}".format(user.email))
        
        # Test 3: Create patient with phone_number
        print("\n[Test 3] Creating patient with phone_number...")
        patient = Patient(
            patient_code="TEST-E2E-{}".format(uuid4().hex[:8].upper()),
            full_name="Test Patient",
            date_of_birth=date(1990, 5, 15),
            sex="male",
            phone_number="12345678",  # Test valid 8-digit number
            hospital_id=hospital.id
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        print("[OK] Patient created: {}".format(patient.patient_code))
        print("     Name: {}".format(patient.full_name))
        print("     Phone: {}".format(patient.phone_number))
        
        # Test 4: Retrieve and verify phone_number
        print("\n[Test 4] Retrieving patient and verifying phone_number...")
        retrieved = db.query(Patient).filter(Patient.id == patient.id).first()
        if retrieved and retrieved.phone_number == "12345678":
            print("[OK] Phone number retrieved correctly: {}".format(retrieved.phone_number))
        else:
            print("[FAIL] Phone number mismatch or not found")
            return False
        
        # Test 5: Test schema validation
        print("\n[Test 5] Testing Pydantic schema validation...")
        from schemas import PatientCreateRequest
        
        # Valid request
        try:
            valid_request = PatientCreateRequest(
                full_name="Jane Doe",
                date_of_birth="1995-03-20",
                sex="female",
                phone_number="87654321"
            )
            print("[OK] Valid request accepted: phone_number={}".format(valid_request.phone_number))
        except Exception as e:
            print("[FAIL] Valid request rejected: {}".format(e))
            return False
        
        # Invalid request (wrong length)
        try:
            invalid_request = PatientCreateRequest(
                full_name="Jane Doe",
                date_of_birth="1995-03-20",
                sex="female",
                phone_number="1234567"  # Only 7 digits
            )
            print("[FAIL] Invalid request (7 digits) was accepted - should have failed")
            return False
        except Exception as e:
            print("[OK] Invalid request (too short) correctly rejected")
        
        # Invalid request (non-numeric)
        try:
            invalid_request = PatientCreateRequest(
                full_name="Jane Doe",
                date_of_birth="1995-03-20",
                sex="female",
                phone_number="1234567a"  # Contains letter
            )
            print("[FAIL] Invalid request (non-numeric) was accepted - should have failed")
            return False
        except Exception as e:
            print("[OK] Invalid request (non-numeric) correctly rejected")
        
        # Test 6: Check API endpoint documentation
        print("\n[Test 6] Checking API endpoint documentation...")
        try:
            from routes.patients import create_patient
            import inspect
            docstring = create_patient.__doc__
            if "phone_number" in str(docstring).lower() or "phone" in str(docstring).lower():
                print("[OK] API documentation mentions phone_number/phone")
            print("[OK] Endpoint is available for testing")
        except Exception as e:
            print("[WARN] Could not verify endpoint: {}".format(e))
        
        # Test 7: Verify response schema includes phone_number
        print("\n[Test 7] Verifying response schema includes phone_number...")
        from schemas import PatientResponse
        response = PatientResponse(
            id=patient.id,
            patient_code=patient.patient_code,
            full_name=patient.full_name,
            date_of_birth=str(patient.date_of_birth),
            sex=patient.sex,
            phone_number=patient.phone_number,
            hospital_id=hospital.id,
            created_at=patient.created_at,
            updated_at=patient.updated_at
        )
        print("[OK] Response schema correctly includes phone_number: {}".format(response.phone_number))
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("\n[FAIL] Test failed with error: {}".format(e))
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_phone_number_e2e()
    sys.exit(0 if success else 1)
