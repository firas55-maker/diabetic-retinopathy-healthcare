#!/usr/bin/env python3
"""
Get the exact hash from the database and test it directly
"""

import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from database import SessionLocal
from models import User
from auth_utils import verify_password, hash_password

db = SessionLocal()

# Get the actual user from DB
user = db.query(User).filter(User.email == 'doctor@hospital.com').first()

if user:
    stored_hash = user.hashed_password
    print("="*80)
    print("HASH FROM DATABASE")
    print("="*80)
    print(f"Full hash: {stored_hash}")
    print(f"Length: {len(stored_hash)}")
    print(f"Type: {type(stored_hash)}")
    print(f"Repr: {repr(stored_hash)}")
    print(f"Hex bytes: {stored_hash.encode().hex()}")

    print("\n" + "="*80)
    print("TESTING verify_password WITH DB HASH")
    print("="*80)

    test_password = "password123"
    result = verify_password(test_password, stored_hash)
    print(f"verify_password('{test_password}', db_hash) = {result}")

    # Also test with a fresh hash
    print("\n" + "="*80)
    print("TESTING WITH FRESHLY CREATED HASH (for comparison)")
    print("="*80)

    fresh_hash = hash_password(test_password)
    fresh_result = verify_password(test_password, fresh_hash)
    print(f"Fresh hash: {fresh_hash}")
    print(f"verify_password('{test_password}', fresh_hash) = {fresh_result}")

    # Check if the DB hash is maybe truncated or altered
    print("\n" + "="*80)
    print("CHARACTER-BY-CHARACTER COMPARISON")
    print("="*80)

    print(f"DB hash length: {len(stored_hash)}")
    print(f"Fresh hash length: {len(fresh_hash)}")

    # Check for any non-ASCII or special characters
    print(f"\nDB hash ASCII check: {all(ord(c) < 128 for c in stored_hash)}")
    print(f"Fresh hash ASCII check: {all(ord(c) < 128 for c in fresh_hash)}")

    # Check the format
    if stored_hash.startswith('$2'):
        print(f"\n✓ DB hash is bcrypt format")
        print(f"  Algorithm: {stored_hash.split('$')[1]}")
        print(f"  Cost: {stored_hash.split('$')[2]}")
    else:
        print(f"\n✗ DB hash is NOT bcrypt format: {stored_hash[:10]}...")

db.close()
