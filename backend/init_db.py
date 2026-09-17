from database import Base, engine, SessionLocal
from models import User, Hospital, Patient, Scan
from auth_utils import hash_password
from models import User, Hospital, Patient, Scan, RoleEnum

Base.metadata.create_all(bind=engine)
print("Tables created")

db = SessionLocal()
hospital = Hospital(name="Test Hospital Cairo", region="Cairo Governorate", city="Cairo")
db.add(hospital)
db.commit()
hospital_id = hospital.id
db.close()
print(f"Hospital created: {hospital_id}")

db = SessionLocal()

doctor = User(
    email="doctor@hospital.com",
    hashed_password=hash_password("SecurePassword123!"),
    full_name="Dr. Ahmed Hassan",
    role=RoleEnum.DOCTOR,
    hospital_id=hospital_id
)
db.add(doctor)

staff = User(
    email="staff@hospital.com",
    hashed_password=hash_password("SecurePassword123!"),
    full_name="Mohamed Ali",
    role=RoleEnum.TECHNICAL_STAFF,
    hospital_id=hospital_id
)
db.add(staff)
db.commit()

patient1 = Patient(full_name="Ahmed Mohamed", date_of_birth="1985-03-15", sex="male", hospital_id=hospital_id, patient_code="PT-001-AHM")
db.add(patient1)
patient2 = Patient(full_name="Fatima Ibrahim", date_of_birth="1990-07-22", sex="female", hospital_id=hospital_id, patient_code="PT-002-FAT")
db.add(patient2)
db.commit()

scan1 = Scan(patient_id=patient1.id, patient_code="PT-001-AHM", ai_grade=2, ai_confidence=0.92, status="reviewed")
db.add(scan1)
scan2 = Scan(patient_id=patient2.id, patient_code="PT-002-FAT", ai_grade=0, ai_confidence=0.87, status="pending_review")
db.add(scan2)
db.commit()
db.close()

print("DOCTOR LOGIN: doctor@hospital.com / SecurePassword123!")
print("STAFF LOGIN: staff@hospital.com / SecurePassword123!")
print("HOSPITAL ID:", hospital_id)
print("PATIENT CODE: PT-001-AHM")
