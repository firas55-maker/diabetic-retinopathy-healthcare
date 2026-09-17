#!/usr/bin/env python3
"""
Check current hash status after migration
"""
import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from auth_utils import hash_password, verify_password

# Test 1: Create a new hash
test_hash = hash_password("password123")
print(f"New hash length: {len(test_hash)}")
print(f"Full hash: {test_hash}")

# Test 2: Verify it works
verify_result = verify_password("password123", test_hash)
print(f"Verification result: {verify_result}")

if len(test_hash) == 60 and verify_result:
    print("\n✓ Hash/verify works correctly")
    print("Ready to re-hash existing user passwords")
else:
    print("\n✗ Issue with hash generation")
