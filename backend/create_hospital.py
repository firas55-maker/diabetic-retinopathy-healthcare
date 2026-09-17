from database import SessionLocal
from models import Hospital
from uuid import uuid4

db = SessionLocal()

new_hospital = Hospital(
    id=uuid4(),
    name="City Medical Center",
    region="East Region",
    city="Boston"
)
db.add(new_hospital)
db.commit()

print(f"Hospital created successfully!")
print(f"ID: {new_hospital.id}")
print(f"Name: {new_hospital.name}")
print(f"\nUse this ID in your registration request:")
print(f"  \"hospital_id\": \"{new_hospital.id}\"")

db.close()
