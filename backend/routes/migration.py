from fastapi import APIRouter, Depends
from sqlalchemy import text
from database import engine
from auth_utils import hash_password
from dependencies import require_admin
from models import User

router = APIRouter()

@router.post("/admin/migrate-hash-column")
async def migrate_hash_column():
    """Temporary migration endpoint - changes hashed_password from VARCHAR(255) to TEXT"""
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                ALTER TABLE users
                ALTER COLUMN hashed_password TYPE TEXT;
            """))
        return {
            "success": True,
            "message": "Migration completed: hashed_password is now TEXT"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/admin/rehash-passwords")
async def rehash_passwords(
    current_user: User = Depends(require_admin)
):
    """Re-hash all user passwords to fix truncated hashes"""
    try:
        with engine.begin() as conn:
            # Get all users
            result = conn.execute(text("SELECT id, email FROM users"))
            users = result.fetchall()

            rehashed_count = 0

            # For now, re-hash with a known password for testing
            # In production, you'd need to know the actual passwords
            test_passwords = {
                "doctor@hospital.com": "password123",
                "doctor2@hospital.com": "password123",
            }

            for user_id, email in users:
                if email in test_passwords:
                    plain_password = test_passwords[email]
                    new_hash = hash_password(plain_password)

                    conn.execute(text("""
                        UPDATE users
                        SET hashed_password = :new_hash
                        WHERE email = :email
                    """), {
                        "new_hash": new_hash,
                        "email": email
                    })
                    rehashed_count += 1

            return {
                "success": True,
                "message": f"Re-hashed {rehashed_count} user password(s)",
                "details": f"Updated passwords for: {', '.join(test_passwords.keys())}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/admin/hospitals")
async def get_hospitals():
    """Get list of all hospitals"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, region, city FROM hospitals LIMIT 20"))
            hospitals = result.fetchall()

            if not hospitals:
                return {
                    "hospitals": [],
                    "count": 0,
                    "message": "No hospitals found"
                }

            return {
                "hospitals": [
                    {
                        "id": str(h[0]),
                        "name": h[1],
                        "region": h[2],
                        "city": h[3]
                    }
                    for h in hospitals
                ],
                "count": len(hospitals)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


