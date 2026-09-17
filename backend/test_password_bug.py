#!/usr/bin/env python3
"""Test script to diagnose password hashing bug"""

import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from auth_utils import hash_password, verify_password

# Test 1: Create a hash and verify immediately
test_password = "password123"
print(f"Test password: {test_password}")

hashed = hash_password(test_password)
print(f"Hash produced: {hashed}")
print(f"Hash type: {type(hashed)}")
print(f"Hash starts with: {hashed[:20] if hashed else 'None'}")

# Test 2: Verify the password
result = verify_password(test_password, hashed)
print(f"\nverify_password('{test_password}', hash) = {result}")

# Test 3: Try with wrong password
wrong_result = verify_password("wrongpassword", hashed)
print(f"verify_password('wrongpassword', hash) = {wrong_result}")

# Test 4: Parse the hash to see what format it is
if hashed.startswith('sha256$'):
    parts = hashed.split('$')
    print(f"\nHash format: SHA256 fallback")
    print(f"  Parts: {len(parts)}")
    print(f"  Salt: {parts[1] if len(parts) > 1 else 'N/A'}")
    print(f"  Hash: {parts[2][:20] if len(parts) > 2 else 'N/A'}...")
elif hashed.startswith('$2'):
    print(f"\nHash format: Bcrypt")
else:
    print(f"\nHash format: Unknown")

print("\n" + "="*60)
if result:
    print("✓ PASSWORD VERIFICATION WORKS - Bug is fixed or elsewhere")
else:
    print("✗ PASSWORD VERIFICATION FAILS - Bug confirmed in hash/verify")
