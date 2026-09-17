#!/usr/bin/env python3
"""
Migration: Change hashed_password column from VARCHAR(255) to TEXT
This fixes the bcrypt hash truncation bug
Uses SQLAlchemy instead of raw psycopg2
"""

import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from sqlalchemy import text
from database import engine

try:
    print("Migrating hashed_password column from VARCHAR(255) to TEXT...")

    with engine.connect() as conn:
        # Alter the column type
        conn.execute(text("""
            ALTER TABLE users
            ALTER COLUMN hashed_password TYPE TEXT;
        """))
        conn.commit()

        print("✓ Migration successful!")
        print("  Column hashed_password is now TEXT")

        # Verify the change
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'hashed_password';
        """)).fetchone()

        if result:
            print(f"✓ Verification: {result[0]} is now {result[1]}")

except Exception as e:
    print(f"✗ Migration failed: {e}")
    import traceback
    traceback.print_exc()
