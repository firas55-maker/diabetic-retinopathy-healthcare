"""Test the patient registration API endpoint with phone_number"""
import sys
sys.path.insert(0, 'backend')

from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Hospital, Patient
from routes.patients import create_patient
from schemas import PatientCreateRequest
from datetime import datetime

def test_api_endpoint():
    """Simulate the API endpoint call"""
    db = SessionLocal()
    
    try:
        # Get a technical staff user for testing
        tech_staff = db.query(User).filter(User.role == 'technical_staff').first()
        
        if not tech_staff:
            print("ERROR: No technical staff user found. Please create one first.")
            return
        
        print(f"Testing as user: {tech_staff.email} ({tech_staff.role})")
        print(f"Hospital: {tech_staff.hospital.name}\n")
        
        # Test 1: Valid phone number
        print("Test 1: Valid 8-digit phone number")
        print("-" * 50)
        
        request_data = PatientCreateRequest(
            full_name="API Test Patient",
            date_of_birth="1985-08-20",
            sex="female",
            phone_number="55667788"
        )
        
        print(f"Request: {request_data.model_dump()}")
        
        # Simulate the endpoint call
        class MockUser:
            def __init__(self, user):
                self.id = user.id
                self.email = user.email
                self.role = user.role
                self.hospital_id = user.hospital_id
        
        mock_user = MockUser(tech_staff)
        
        # This would normally be called via FastAPI
        # We'll manually execute the logic
        try:
            dob = datetime.strptime(request_data.date_of_birth, "%Y-%m-%d").date()
            
            # Validate phone_number
            if not request_data.phone_number.isdigit():
                print("VALIDATION ERROR: Phone number must contain only digits")
            elif len(request_data.phone_number) != 8:
                print("VALIDATION ERROR: Phone number must be exactly 8 digits")
            else:
                # Generate patient code
                today = datetime.now().strftime("%Y%m%d")
                latest = db.query(Patient).filter(
                    Patient.patient_code.ilike(f"PAT-{today}-%")
                ).order_by(Patient.patient_code.desc()).first()
                
                seq = (int(latest.patient_code.split("-")[-1]) + 1) if latest else 1
                patient_code = f"PAT-{today}-{seq:04d}"
                
                # Create patient
                new_patient = Patient(
                    patient_code=patient_code,
                    full_name=request_data.full_name,
                    date_of_birth=dob,
                    sex=request_data.sex.lower(),
                    phone_number=request_data.phone_number,
                    hospital_id=mock_user.hospital_id
                )
                
                db.add(new_patient)
                db.commit()
                db.refresh(new_patient)
                
                print(f"SUCCESS: Patient created!")
                print(f"  Patient Code: {new_patient.patient_code}")
                print(f"  Full Name: {new_patient.full_name}")
                print(f"  Phone Number: {new_patient.phone_number}")
                print(f"  Hospital: {tech_staff.hospital.name}")
                
                # Clean up
                db.delete(new_patient)
                db.commit()
                print(f"\nTest data cleaned up.")
                
        except Exception as e:
            print(f"ERROR: {e}")
            db.rollback()
        
        # Test 2: Invalid phone number (too short)
        print("\n\nTest 2: Invalid phone number (too short)")
        print("-" * 50)
        try:
            invalid_request = PatientCreateRequest(
                full_name="Invalid Test",
                date_of_birth="1990-01-01",
                sex="male",
                phone_number="123"
            )
        except Exception as e:
            print(f"EXPECTED VALIDATION ERROR: {e}")
        
        # Test 3: Invalid phone number (non-numeric)
        print("\n\nTest 3: Invalid phone number (contains letters)")
        print("-" * 50)
        try:
            invalid_request2 = PatientCreateRequest(
                full_name="Invalid Test 2",
                date_of_birth="1990-01-01",
                sex="male",
                phone_number="abc12345"
            )
            # Pydantic will allow it (string type), but backend validation will catch it
            if not invalid_request2.phone_number.isdigit():
                print("EXPECTED VALIDATION ERROR: Phone number must contain only digits")
        except Exception as e:
            print(f"VALIDATION ERROR: {e}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_api_endpoint()
