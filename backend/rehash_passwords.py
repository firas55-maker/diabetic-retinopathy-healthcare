#!/usr/bin/env python3
"""
Re-hash all user passwords in the database
This fixes hashes that were truncated before the TEXT column migration
"""
import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from auth_utils import hash_password
from sqlalchemy import text
from database import engine

# Dictionary of email -> password for users we want to re-hash
# Add entries for each user that needs re-hashing
users_to_rehash = {
    "doctor@hospital.com": "password123",
    "doctor2@hospital.com": "password123",  # Assuming same password format
}

print("Re-hashing user passwords...")
print("="*70)

try:
    with engine.begin() as conn:
        for email, plain_password in users_to_rehash.items():
            # Create new hash
            new_hash = hash_password(plain_password)

            print(f"\nEmail: {email}")
            print(f"  New hash length: {len(new_hash)}")
            print(f"  New hash: {new_hash[:40]}...")

            # Update the database
            conn.execute(text("""
                UPDATE users
                SET hashed_password = :new_hash
                WHERE email = :email
            """), {
                "new_hash": new_hash,
                "email": email
            })

            print(f"  ✓ Updated in database")

    print("\n" + "="*70)
    print("✓ Re-hashing complete!")
    print("\nNow test login with:")
    print("  Email: doctor@hospital.com")
    print("  Password: password123")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
