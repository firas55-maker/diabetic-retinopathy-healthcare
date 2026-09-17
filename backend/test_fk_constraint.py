from database import SessionLocal
from models import Hospital, User, RoleEnum
from auth_utils import hash_password
from uuid import UUID

db = SessionLocal()

# Test: Try to create a user with a non-existent hospital_id
print("=== TEST: Creating user with non-existent hospital_id ===")

new_email = f"test.user.{UUID(int=0).hex[:8]}@hospital.com"
fake_hospital_id = "550e8400-e29b-41d4-a716-446655440000"

try:
    hashed_password = hash_password("testpassword123")
    new_user = User(
        email=new_email,
        hashed_password=hashed_password,
        full_name="Test User",
        role=RoleEnum.DOCTOR,
        hospital_id=UUID(fake_hospital_id),
        specialty="Testing"
    )

    print(f"1. User object created in memory")
    print(f"   Email: {new_user.email}")
    print(f"   Hospital ID: {new_user.hospital_id}")

    db.add(new_user)
    print(f"2. User added to session")

    db.commit()
    print(f"3. COMMIT successful - user inserted into database")
    print(f"   User ID: {new_user.id}")

    db.refresh(new_user)
    print(f"4. REFRESH successful")
    print(f"   Refreshed user email: {new_user.email}")

except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")
    db.rollback()

db.close()
