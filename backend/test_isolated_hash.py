#!/usr/bin/env python3
"""
ISOLATED TEST: hash_password() and verify_password()
No database, no API, no FastAPI — just the pure functions
"""

import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from auth_utils import hash_password, verify_password

print("="*80)
print("ISOLATED TEST: hash_password() + verify_password()")
print("="*80)

test_password = "password123"

print(f"\n1. Creating hash for: '{test_password}'")
created_hash = hash_password(test_password)
print(f"   Hash created: {created_hash}")
print(f"   Hash length: {len(created_hash)}")

print(f"\n2. Immediately verifying: verify_password('{test_password}', created_hash)")
result = verify_password(test_password, created_hash)
print(f"   Result: {result}")

print("\n" + "="*80)
if result is True:
    print("✓ TEST PASSED: verify_password() returned True")
elif result is False:
    print("✗ TEST FAILED: verify_password() returned False")
    print("  BUG CONFIRMED: hash_password() and verify_password() are incompatible")
else:
    print(f"? UNEXPECTED: verify_password() returned {type(result)}: {result}")
print("="*80)
