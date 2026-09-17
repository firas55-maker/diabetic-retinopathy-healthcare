-- Migration: Add phone_number column to patients table
-- Date: 2026-09-17

-- Add phone_number column (nullable initially to allow existing rows)
ALTER TABLE patients ADD COLUMN IF NOT EXISTS phone_number VARCHAR(8);

-- Note: For production, you would need to:
-- 1. Add the column as nullable
-- 2. Update existing rows with default/placeholder values
-- 3. Then alter the column to NOT NULL
-- 
-- Example:
-- UPDATE patients SET phone_number = '00000000' WHERE phone_number IS NULL;
-- ALTER TABLE patients ALTER COLUMN phone_number SET NOT NULL;
