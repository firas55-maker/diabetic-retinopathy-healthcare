#!/usr/bin/env python3
"""
Test login to capture any errors
"""

import requests
import json

login_data = {
    "email": "doctor@hospital.com",
    "password": "SecurePassword123!"
}

print("=" * 80)
print("Testing POST /auth/login")
print("=" * 80)
print()

print(f"Request body:")
print(json.dumps(login_data, indent=2))
print()

response = requests.post(
    "http://localhost:8000/auth/login",
    json=login_data,
    timeout=5
)

print(f"Status: {response.status_code}")
print()
print(f"Response:")
print(json.dumps(response.json(), indent=2))
