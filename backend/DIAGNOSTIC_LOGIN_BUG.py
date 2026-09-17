#!/usr/bin/env python3
"""
COMPREHENSIVE DIAGNOSTIC for the 401 bug

Since we can't connect to the database right now, this script will:
1. Confirm password hashing works (already done)
2. Check for any issues in the login route logic itself
3. Identify what WOULD cause 401 given the code structure
"""

import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\Desktop\\helathcare 2\\backend')

from auth_utils import hash_password, verify_password

print("="*80)
print("ANALYZING LOGIN ROUTE LOGIC (from auth.py lines 90-124)")
print("="*80)

print("""
The login route does:

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    # Line 103
    user = db.query(User).filter(User.email == request.email).first()

    # Line 104
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

A 401 response means ONE of these happened:
  A) user is None (email not found in DB)
  B) verify_password() returned False

Since your test showed verify_password() works correctly,
the issue is most likely A) - the user is not being found.
""")

print("\n" + "="*80)
print("POSSIBLE ROOT CAUSES FOR 'USER NOT FOUND'")
print("="*80)

causes = [
    {
        "title": "Email case mismatch",
        "description": "User stored as 'Doctor@Hospital.com' but query is 'doctor@hospital.com'",
        "likelihood": "LOW - EmailStr normalizes to lowercase",
        "how_to_test": "SELECT email FROM users WHERE id=... (check exact value in DB)"
    },
    {
        "title": "Email has whitespace",
        "description": "User stored as 'doctor@hospital.com ' (trailing space)",
        "likelihood": "MEDIUM - possible if manual INSERT didn't strip",
        "how_to_test": "SELECT email, length(email) FROM users WHERE email LIKE 'doctor@%'"
    },
    {
        "title": "Password string has encoding issues",
        "description": "Password in request has BOM, UTF-8 encoding issues, or trailing newline",
        "likelihood": "MEDIUM - JSON encoding edge case",
        "how_to_test": "Log request.password bytes: print(request.password.encode())"
    },
    {
        "title": "Stored hash got corrupted",
        "description": "Hash stored as VARCHAR(255) but bcrypt hash is >255 chars, got truncated",
        "likelihood": "HIGH - bcrypt hashes are ~60 chars, but could be issue",
        "how_to_test": "SELECT length(hashed_password) FROM users WHERE email='doctor@hospital.com'"
    },
    {
        "title": "User exists but in wrong hospital context",
        "description": "Some row-level security or scoping filtering user out",
        "likelihood": "LOW - no such code visible",
        "how_to_test": "Check if there are any WHERE filters before the login query"
    },
    {
        "title": "Database transaction not committed",
        "description": "Your manual script committed, but maybe to wrong database/schema",
        "likelihood": "MEDIUM - different database connections",
        "how_to_test": "Verify DATABASE_URL and psql into it manually: SELECT * FROM users"
    },
    {
        "title": "Typo in email when manually updating",
        "description": "Script said 'doctor@hospital.com' but actually stored 'docto@hospital.com'",
        "likelihood": "LOW - but human error is always possible",
        "how_to_test": "SELECT * FROM users WHERE email LIKE '%doctor%' OR email LIKE '%hospital%'"
    },
]

for i, cause in enumerate(causes, 1):
    print(f"\n[{i}] {cause['title']}")
    print(f"    Description: {cause['description']}")
    print(f"    Likelihood: {cause['likelihood']}")
    print(f"    How to test: {cause['how_to_test']}")

print("\n" + "="*80)
print("NEXT STEPS - DO THIS IN ORDER")
print("="*80)

steps = """
1. Start PostgreSQL (if not running):
   - Windows: net start postgresql-x64-##
   - Or use Docker: docker run -e POSTGRES_PASSWORD=password -p 5432:5432 postgres

2. Connect to the database and run these queries:

   -- Check if the user exists
   SELECT * FROM users WHERE email = 'doctor@hospital.com';

   -- Check length of password hash (should be ~60)
   SELECT email, length(hashed_password) as hash_len, hashed_password FROM users;

   -- Check for similar emails (whitespace, case issues)
   SELECT email, length(email) FROM users WHERE email ILIKE '%doctor%hospital%';

3. If user exists, manually test the hash in Python:
   - Copy the hashed_password value from DB
   - Run this in Python:
     from auth_utils import verify_password
     result = verify_password('password123', 'PASTE_HASH_HERE')
     print(result)

4. If password verification passes, test the login endpoint in Swagger/curl:
   curl -X POST http://localhost:8000/auth/login \\
     -H "Content-Type: application/json" \\
     -d '{"email":"doctor@hospital.com","password":"password123"}'

5. If still fails, add DEBUG logging to auth.py line 103-104:
   print(f"Looking for user with email: {request.email}")
   print(f"Query result: {user}")
   if user:
       verify_result = verify_password(request.password, user.hashed_password)
       print(f"Password verify result: {verify_result}")
"""

print(steps)

print("\n" + "="*80)
print("WHAT I'VE CONFIRMED SO FAR")
print("="*80)
print("""
✓ hash_password() creates valid bcrypt hashes
✓ verify_password() correctly verifies passwords
✓ Wrong passwords are correctly rejected
✓ The code logic appears sound

✗ UNKNOWN: Whether the user actually exists in DB with correct email
✗ UNKNOWN: Whether the hash got stored correctly in DB
✗ UNKNOWN: Whether there are any encoding/truncation issues
""")
