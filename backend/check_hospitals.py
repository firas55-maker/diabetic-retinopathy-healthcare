from database import SessionLocal
from models import Hospital, User

db = SessionLocal()

# Check hospitals
print("=== HOSPITALS TABLE ===")
hospitals = db.query(Hospital).all()
if hospitals:
    for h in hospitals:
        print(f"  ID: {h.id}")
        print(f"  Name: {h.name}")
else:
    print("  (empty)")

# Check the hospital_id from the user's example request
test_hospital_id = "550e8400-e29b-41d4-a716-446655440000"
print(f"\n=== CHECKING TEST HOSPITAL ID ===")
print(f"Looking for: {test_hospital_id}")

exists = db.query(Hospital).filter(Hospital.id == test_hospital_id).first()
if exists:
    print(f"✓ Found: {exists.name}")
else:
    print(f"✗ NOT FOUND")

# Check users and their hospital_ids
print("\n=== USERS AND THEIR HOSPITAL_IDS ===")
users = db.query(User).all()
for u in users:
    hospital = db.query(Hospital).filter(Hospital.id == u.hospital_id).first()
    hospital_name = hospital.name if hospital else "MISSING HOSPITAL"
    print(f"  {u.email} -> {u.hospital_id} ({hospital_name})")

db.close()
