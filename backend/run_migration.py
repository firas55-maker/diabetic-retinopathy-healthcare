#!/usr/bin/env python3
"""
Run migration through a temporary FastAPI endpoint
"""

import requests
import json

# First, create the migration endpoint in the server
# by making a request to trigger it

migration_code = '''
from sqlalchemy import text
from database import engine

def run_migration():
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                ALTER TABLE users
                ALTER COLUMN hashed_password TYPE TEXT;
            """))
        return {"success": True, "message": "Migration completed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

result = run_migration()
print(json.dumps(result))
'''

print("Running migration through FastAPI server...")
print("Executing: ALTER TABLE users ALTER COLUMN hashed_password TYPE TEXT;")

import subprocess
import sys

result = subprocess.run([
    sys.executable, "-c",
    f"""
import sys
sys.path.insert(0, 'C:\\\\Users\\\\LENOVO\\\\Desktop\\\\helathcare 2\\\\backend')
from sqlalchemy import text, create_engine
from config import settings

engine = create_engine(settings.DATABASE_URL)
try:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ALTER COLUMN hashed_password TYPE TEXT;"))
    print("✓ Migration successful!")
except Exception as e:
    print(f"✗ Migration failed: {{e}}")
"""
], capture_output=True, text=True, cwd="C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend")

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print(f"Exit code: {result.returncode}")
