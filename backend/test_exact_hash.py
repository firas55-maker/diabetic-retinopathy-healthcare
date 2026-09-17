#!/usr/bin/env python3
"""
Test the EXACT hash you reported from the database
"""

import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from auth_utils import verify_password

# From your data: doctor@hospital.com hash prefix is $2b$12$bHYEVYmOU2C/Z
# But we need the FULL 60-char hash
# The debug log shows: $2b$12$bHYEVYmOU2C/ZZZQkyAXyu3OqVxgMjUFn

full_hash_from_debug = "$2b$12$bHYEVYmOU2C/ZZZQkyAXyu3OqVxgMjUFn"

print("="*80)
print("Testing with FULL hash from login debug log")
print("="*80)
print(f"Hash: {full_hash_from_debug}")
print(f"Length: {len(full_hash_from_debug)}")

test_password = "password123"
result = verify_password(test_password, full_hash_from_debug)

print(f"\nverify_password('{test_password}', hash) = {result}")

if not result:
    print("\n✗ CONFIRMED: This hash was NOT created with 'password123'")
    print("  The hash in the database was created with a DIFFERENT password")
else:
    print("\n✓ Hash matches password123")
