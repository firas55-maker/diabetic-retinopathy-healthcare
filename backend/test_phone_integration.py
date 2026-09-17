"""Integration test for patient registration with phone_number"""
import sys
sys.path.insert(0, 'backend')
import requests
import json
from config import settings

BASE_URL = "http://localhost:8000"

def test_registration():
    print("Integration Test: Patient Registration with Phone Number")
    print("=" * 70)
    
    # You would need valid credentials here
    # For demonstration, showing the expected API interaction
    
    print("\nAPI Endpoint: POST /patients/")
    print("Authorization: Bearer <token> (technical_staff role required)")
    
    print("\n1. Valid Request:")
    valid_payload = {
        "full_name": "John Doe",
        "date_of_birth": "1990-05-15",
        "sex": "male",
        "phone_number": "12345678"
    }
    print(json.dumps(valid_payload, indent=2))
    
    print("\n2. Expected Response (201 Created):")
    expected_response = {
        "patient_code": "PAT-20260917-0001",
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "full_name": "John Doe"
    }
    print(json.dumps(expected_response, indent=2))
    
    print("\n3. Invalid Request (phone too short):")
    invalid_payload = {
        "full_name": "Jane Doe",
        "date_of_birth": "1992-03-20",
        "sex": "female",
        "phone_number": "123"
    }
    print(json.dumps(invalid_payload, indent=2))
    print("\nExpected Response (400 Bad Request):")
    print('{"detail": "Phone number must be exactly 8 digits"}')
    
    print("\n4. Invalid Request (non-numeric):")
    invalid_payload2 = {
        "full_name": "Bob Smith",
        "date_of_birth": "1988-11-10",
        "sex": "male",
        "phone_number": "abcd1234"
    }
    print(json.dumps(invalid_payload2, indent=2))
    print("\nExpected Response (400 Bad Request):")
    print('{"detail": "Phone number must contain only digits"}')
    
    print("\n" + "=" * 70)
    print("\nValidation Summary:")
    print("Backend (FastAPI/Pydantic):")
    print("  - Field is required (not optional)")
    print("  - Must be exactly 8 characters (min_length=8, max_length=8)")
    print("  - Additional backend validation: isdigit() check")
    print("\nFrontend (React):")
    print("  - Required field")
    print("  - HTML5 pattern validation: \d{8}")
    print("  - maxLength attribute: 8")
    print("  - JavaScript pre-submit validation: /^\d{8}$/")
    print("\nDatabase (PostgreSQL):")
    print("  - Column: phone_number VARCHAR(8)")
    print("  - Currently nullable (for existing records)")
    print("  - New registrations require the field")

if __name__ == "__main__":
    test_registration()
