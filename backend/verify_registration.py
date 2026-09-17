from database import SessionLocal
from models import User

db = SessionLocal()

user = db.query(User).filter(User.email == "newuser.test@hospital.com").first()

if user:
    print("✓ User found in database!")
    print(f"  Email: {user.email}")
    print(f"  Full Name: {user.full_name}")
    print(f"  Role: {user.role.value}")
    print(f"  Hospital ID: {user.hospital_id}")
    print(f"  Specialty: {user.specialty}")
    print(f"  User ID: {user.id}")
else:
    print("✗ User not found")

db.close()
