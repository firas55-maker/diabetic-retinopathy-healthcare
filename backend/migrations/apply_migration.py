"""Apply database migration: Add phone_number column to patients table"""
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from config import settings

def apply_migration():
    """Apply the phone_number column migration"""
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='patients' AND column_name='phone_number'
        """))
        
        if result.fetchone():
            print("✓ Column 'phone_number' already exists in patients table")
            return
        
        # Add the column (nullable first to allow existing rows)
        print("Adding phone_number column to patients table...")
        conn.execute(text("ALTER TABLE patients ADD COLUMN phone_number VARCHAR(8)"))
        conn.commit()
        
        print("✓ Successfully added phone_number column")
        print("\nNote: Column is nullable. For new patient registrations, it will be required.")
        print("Existing patients will have NULL phone_number until updated.")

if __name__ == "__main__":
    try:
        apply_migration()
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        sys.exit(1)
