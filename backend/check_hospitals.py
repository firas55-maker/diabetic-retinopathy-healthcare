#!/usr/bin/env python3
"""
Query the database to find existing hospitals
"""
import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from sqlalchemy import text
from database import engine

try:
    with engine.begin() as conn:
        result = conn.execute(text("SELECT id, name, region, city FROM hospitals LIMIT 10"))
        hospitals = result.fetchall()

        if hospitals:
            print("Existing hospitals:")
            print("="*80)
            for hospital_id, name, region, city in hospitals:
                print(f"ID: {hospital_id}")
                print(f"   Name: {name}")
                print(f"   Region: {region}")
                print(f"   City: {city}\n")
        else:
            print("No hospitals found in database")
            print("\nYou need to create a hospital first. Here's a sample:")
            print("""
curl -X POST http://localhost:8000/hospitals \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Central Medical Hospital",
    "region": "North Region",
    "city": "New York"
  }'
            """)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
