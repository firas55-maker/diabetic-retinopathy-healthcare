#!/usr/bin/env python3
"""
Test script to verify GET /patients/ and GET /doctor/scans/{scan_id}/image endpoints
Run this after starting the backend: python test_endpoints.py
"""

import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(message, status="info"):
    if status == "success":
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    elif status == "error":
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    else:
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def test_login():
    """Test login to get JWT token"""
    print("\n" + "="*60)
    print("STEP 1: Testing Authentication (GET JWT Token)")
    print("="*60)

    # Try multiple credentials
    credentials = [
        {"email": "doctor1@hospital.com", "password": "password123"},
        {"email": "admin@hospital.com", "password": "password123"},
        {"email": "staff@hospital.com", "password": "password123"},
    ]

    for cred in credentials:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=cred,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print_status(f"Login successful with {cred['email']}", "success")
                print(f"   Token: {token[:50]}...")
                return token
            else:
                print_status(f"Login failed with {cred['email']}: {response.status_code}", "warning")
        except Exception as e:
            print_status(f"Error testing {cred['email']}: {str(e)}", "warning")

    print_status("Could not authenticate with any credentials", "error")
    return None

def test_get_patients(token):
    """Test GET /patients/ endpoint"""
    print("\n" + "="*60)
    print("STEP 2: Testing GET /patients/ Endpoint")
    print("="*60)

    if not token:
        print_status("No token available, skipping test", "warning")
        return False

    try:
        response = requests.get(
            f"{BASE_URL}/patients/?skip=0&limit=50",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )

        print(f"Request: GET /patients/?skip=0&limit=50")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_status(f"GET /patients/ returned 200 OK", "success")
            print(f"   Response type: {type(data)}")
            print(f"   Response length: {len(data) if isinstance(data, list) else 'N/A'}")

            if isinstance(data, list) and len(data) > 0:
                print(f"   First patient: {json.dumps(data[0], indent=4, default=str)}")
            else:
                print(f"   Response: {json.dumps(data, indent=4, default=str)[:200]}...")

            return True
        elif response.status_code == 405:
            print_status("GET /patients/ returned 405 Method Not Allowed", "error")
            print(f"   This means the backend hasn't reloaded the GET endpoint")
            print(f"   Response: {response.text}")
            return False
        else:
            print_status(f"GET /patients/ returned {response.status_code}", "warning")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print_status("Could not connect to backend at localhost:8000", "error")
        print("   Make sure backend is running: python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print_status(f"Error testing GET /patients/: {str(e)}", "error")
        return False

def test_get_scan_image(token):
    """Test GET /doctor/scans/{scan_id}/image endpoint"""
    print("\n" + "="*60)
    print("STEP 3: Testing GET /doctor/scans/{scan_id}/image Endpoint")
    print("="*60)

    if not token:
        print_status("No token available, skipping test", "warning")
        return False

    # First, get a scan from the queue
    try:
        print("Fetching scan queue to find a scan_id...")
        queue_response = requests.get(
            f"{BASE_URL}/doctor/scans/queue?skip=0&limit=1",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )

        if queue_response.status_code != 200:
            print_status(f"Could not fetch scan queue: {queue_response.status_code}", "warning")
            print("   Skipping image endpoint test (no scans available)")
            return None

        queue_data = queue_response.json()
        scans = queue_data.get("scans", []) if isinstance(queue_data, dict) else []

        if not scans:
            print_status("No scans available in queue", "warning")
            print("   Upload a scan first to test the image endpoint")
            return None

        scan_id = scans[0]["id"]
        print(f"Found scan_id: {scan_id}")

        # Now test the image endpoint
        print(f"\nRequest: GET /doctor/scans/{scan_id}/image")
        image_response = requests.get(
            f"{BASE_URL}/doctor/scans/{scan_id}/image",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )

        print(f"Status Code: {image_response.status_code}")
        print(f"Content-Type: {image_response.headers.get('content-type', 'Not set')}")
        print(f"Content-Length: {len(image_response.content)} bytes")

        if image_response.status_code == 200:
            print_status(f"GET /doctor/scans/{{scan_id}}/image returned 200 OK", "success")
            print(f"   Image data received: {len(image_response.content)} bytes")
            print(f"   Content-Type: {image_response.headers.get('content-type')}")
            return True
        elif image_response.status_code == 404:
            print_status(f"GET /doctor/scans/{{scan_id}}/image returned 404 Not Found", "error")
            detail = image_response.json().get("detail", "Unknown error")
            print(f"   Detail: {detail}")
            return False
        else:
            print_status(f"GET /doctor/scans/{{scan_id}}/image returned {image_response.status_code}", "warning")
            print(f"   Response: {image_response.text[:200]}...")
            return False

    except requests.exceptions.ConnectionError:
        print_status("Could not connect to backend", "error")
        return False
    except Exception as e:
        print_status(f"Error testing GET /doctor/scans/{{scan_id}}/image: {str(e)}", "error")
        return False

def check_backend_status():
    """Check if backend is running"""
    print("\n" + "="*60)
    print("INITIAL CHECK: Backend Status")
    print("="*60)

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print_status("Backend is running", "success")
            return True
    except:
        pass

    print_status("Backend is not responding", "error")
    print("Start the backend with:")
    print("  cd C:\\Users\\LENOVO\\Desktop\\helathcare\\ 2\\backend")
    print("  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    return False

def main():
    print("\n" + "="*60)
    print("HEALTHCARE API ENDPOINT TEST")
    print("="*60)

    # Check backend is running
    if not check_backend_status():
        sys.exit(1)

    # Test login
    token = test_login()
    if not token:
        print("\n" + "="*60)
        print("Cannot proceed without authentication")
        print("="*60)
        sys.exit(1)

    # Test endpoints
    patients_ok = test_get_patients(token)
    image_ok = test_get_scan_image(token)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    print(f"GET /patients/: {'✅ PASS' if patients_ok else '❌ FAIL'}")
    print(f"GET /doctor/scans/{{scan_id}}/image: {'✅ PASS' if image_ok else ('⏭️  SKIPPED' if image_ok is None else '❌ FAIL')}")

    if patients_ok and (image_ok or image_ok is None):
        print_status("\nAll tests passed!", "success")
        sys.exit(0)
    else:
        print_status("\nSome tests failed - see details above", "error")
        sys.exit(1)

if __name__ == "__main__":
    main()
