#!/usr/bin/env python3
"""
Reproduce the exact bug scenario:
1. Simulate your manual script: create a hash with hash_password()
2. Simulate storing it in the database (just keep it in a variable)
3. Simulate the login route: query and verify_password()
This isolates the password logic from database/session issues.
"""

import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from auth_utils import hash_password, verify_password

print("="*70)
print("REPRODUCING BUG SCENARIO (without database)")
print("="*70)

# Scenario from user's report
test_password = "password123"

print("\n[1] Your manual script runs:")
print(f"    password = '{test_password}'")
print(f"    u.hashed_password = hash_password(password)")

# This is what your script did
stored_hash = hash_password(test_password)
print(f"\n    Result stored in DB: {stored_hash[:40]}...")

print("\n[2] Immediately after, login endpoint receives request with same password")
print(f"    POST /auth/login")
print(f"    {{\"email\": \"doctor@hospital.com\", \"password\": \"{test_password}\"}}")

print("\n[3] Login route does (line 104 of auth.py):")
print(f"    user = db.query(User).filter(User.email == request.email).first()")
print(f"    if not user or not verify_password(request.password, user.hashed_password):")
print(f"        raise 401")

print("\n    Simulating with stored hash from step [1]:")
verify_result = verify_password(test_password, stored_hash)

print(f"\n    verify_password('{test_password}', stored_hash)")
print(f"    = {verify_result}")

print("\n" + "="*70)
if verify_result:
    print("✓ RESULT: Password verification WORKS")
    print("  This means the bug is NOT in hash_password/verify_password")
    print("  The bug is likely in:")
    print("  - Database session/caching (stale user object)")
    print("  - Email not matching (case sensitivity, whitespace)")
    print("  - Data type mismatch (hash stored as wrong type)")
else:
    print("✗ RESULT: Password verification FAILS")
    print("  Bug confirmed in hash_password/verify_password logic")
print("="*70)

# Additional diagnostics
print("\n[DIAGNOSIS] Hash format analysis:")
if stored_hash.startswith('$2'):
    print(f"  ✓ Using BCRYPT (starts with $2)")
    print(f"    Full hash: {stored_hash}")
elif stored_hash.startswith('sha256$'):
    print(f"  ✓ Using SHA256 FALLBACK (starts with sha256$)")
    parts = stored_hash.split('$')
    print(f"    Salt: {parts[1][:16]}...")
    print(f"    Hash: {parts[2][:16]}...")
else:
    print(f"  ? Unknown format: {stored_hash[:20]}...")

# Test wrong password to ensure verify_password rejects it
print("\n[SANITY CHECK] Testing with WRONG password:")
wrong_verify = verify_password("wrongpassword", stored_hash)
print(f"  verify_password('wrongpassword', stored_hash) = {wrong_verify}")
if not wrong_verify:
    print("  ✓ Correctly rejects wrong password")
else:
    print("  ✗ BUG: Accepts wrong password!")
