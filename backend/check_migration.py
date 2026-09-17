import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text, inspect
from config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)
inspector = inspect(engine)

columns = inspector.get_columns('patients')
print("Patients table columns:")
for col in columns:
    print(f"  - {col['name']}: {col['type']}")
    
phone_col = [c for c in columns if c['name'] == 'phone_number']
if phone_col:
    print("\n[OK] phone_number column exists!")
else:
    print("\n[ERROR] phone_number column not found")
