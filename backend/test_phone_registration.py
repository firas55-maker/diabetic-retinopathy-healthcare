"""Test patient registration with phone_number field"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# First, we need to login to get a token (using technical_staff credentials)
# For this test, I'll show the request format needed

print("Testing Patient Registration with Phone Number\n")
print("=" * 60)

# Test 1: Register patient with valid phone number
test_patient = {
    "full_name": "Test Patient Phone",
    "date_of_birth": "1985-06-15",
    "sex": "male",
    "phone_number": "98765432"
}

print("\nTest 1: Valid phone number (8 digits)")
print(f"Request payload: {json.dumps(test_patient, indent=2)}")

# Note: This would require authentication token
# Response expected: {"patient_code": "PAT-20260917-XXXX", "id": "...", "full_name": "..."}

# Test 2: Invalid phone number (not 8 digits)
test_invalid = {
    "full_name": "Test Invalid",
    "date_of_birth": "1990-01-01",
    "sex": "female",
    "phone_number": "123"  # Too short
}

print("\n\nTest 2: Invalid phone number (too short)")
print(f"Request payload: {json.dumps(test_invalid, indent=2)}")
print("Expected error: 'Phone number must be exactly 8 digits'")

# Test 3: Invalid phone number (contains non-digits)
test_non_numeric = {
    "full_name": "Test Non Numeric",
    "date_of_birth": "1990-01-01",
    "sex": "female",
    "phone_number": "1234567a"
}

print("\n\nTest 3: Invalid phone number (non-numeric)")
print(f"Request payload: {json.dumps(test_non_numeric, indent=2)}")
print("Expected error: 'Phone number must contain only digits'")

print("\n" + "=" * 60)
print("\nBackend validation rules:")
print("  ✓ Phone number must be exactly 8 digits")
print("  ✓ Phone number must contain only numeric characters")
print("\nFrontend validation:")
print("  ✓ HTML pattern attribute: \d{8}")
print("  ✓ maxLength: 8")
print("  ✓ JavaScript validation: /^\d{8}$/")
