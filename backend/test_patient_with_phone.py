"""End-to-end test: Create patient with phone number"""
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Patient, User, Hospital
from datetime import date

# Create engine and session
engine = create_engine(settings.DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

def test_patient_creation():
    """Test creating a patient with phone_number"""
    session = Session()
    
    try:
        # Get a hospital to use
        hospital = session.query(Hospital).first()
        if not hospital:
            print("ERROR: No hospital found in database. Please seed data first.")
            return
        
        print(f"Using hospital: {hospital.name}")
        
        # Create a test patient directly in the database
        test_patient = Patient(
            patient_code=f"PAT-TEST-{int(__import__('time').time())}",
            full_name="Test Patient With Phone",
            date_of_birth=date(1990, 5, 15),
            sex="male",
            phone_number="98765432",
            hospital_id=hospital.id
        )
        
        session.add(test_patient)
        session.commit()
        session.refresh(test_patient)
        
        print("\nPatient created successfully!")
        print(f"  Patient Code: {test_patient.patient_code}")
        print(f"  Full Name: {test_patient.full_name}")
        print(f"  Date of Birth: {test_patient.date_of_birth}")
        print(f"  Sex: {test_patient.sex}")
        print(f"  Phone Number: {test_patient.phone_number}")
        print(f"  Hospital ID: {test_patient.hospital_id}")
        
        # Verify it was saved
        retrieved = session.query(Patient).filter_by(
            patient_code=test_patient.patient_code
        ).first()
        
        if retrieved and retrieved.phone_number == "98765432":
            print("\n[SUCCESS] Patient with phone number retrieved from database!")
            print(f"  Retrieved phone_number: {retrieved.phone_number}")
        else:
            print("\n[ERROR] Could not retrieve patient or phone_number mismatch")
        
        # Clean up test data
        session.delete(test_patient)
        session.commit()
        print("\nTest data cleaned up.")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    test_patient_creation()
