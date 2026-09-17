# Backend Endpoint Fixes - Verification & Testing Guide

## Summary of Changes

### 1. GET /patients/ Endpoint ✅ ADDED

**Location**: `backend/routes/patients.py` (lines 108-130)

**Implementation**:
```python
@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[PatientResponse]:
```

**What it does**:
- Returns all patients from the current user's hospital
- Supports pagination via `skip` and `limit` query parameters
- Requires authentication (any authenticated user can list their hospital's patients)
- Returns ordered by creation date (newest first)

**Request**: `GET /patients/?skip=0&limit=50`

**Response**: Array of PatientResponse objects
```json
[
  {
    "id": "uuid-string",
    "patient_code": "PAT-20260917-0001",
    "full_name": "Jane Smith",
    "date_of_birth": "1990-05-15",
    "sex": "female",
    "hospital_id": "uuid-string",
    "created_at": "2026-09-17T01:00:00",
    "updated_at": "2026-09-17T01:00:00"
  }
]
```

---

### 2. GET /doctor/scans/{scan_id}/image Endpoint ✅ VERIFIED

**Location**: `backend/routes/doctor.py` (lines 164-214)

**Implementation**:
```python
@router.get("/scans/{scan_id}/image")
async def get_scan_image(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
```

**What it does**:
- Returns the actual image file bytes from disk
- Requires doctor authentication
- Validates authorization (doctor can only view scans from their hospital)
- Returns 404 if scan not found
- Returns 404 if image file missing from disk
- Returns 403 if user not authorized
- Correctly sets Content-Type based on file extension (JPEG, PNG, WebP)

**Request**: `GET /doctor/scans/{scan_id}/image`

**Response**: Binary image file with correct `Content-Type` header

---

## Why You're Getting 405/404 Errors

### 405 Method Not Allowed on GET /patients/

**Possible causes**:
1. ✅ Code is correct - GET endpoint is defined at line 108
2. **Backend process NOT restarted** - This is the most likely cause
3. Stale imports or module caching

**Fix**: Restart the backend process to reload the routes

### 404 Not Found on GET /doctor/scans/{scan_id}/image

**Possible causes**:
1. ✅ Endpoint exists (lines 164-214 in doctor.py)
2. Specific scan doesn't exist in database
3. Image file doesn't exist at the path stored in database
4. Path resolution issue (absolute vs relative paths)

**Expected behavior**:
- If scan exists and file exists: 200 OK + image bytes
- If scan doesn't exist: 404 "Scan not found"
- If file missing: 404 "Image file not found on disk"
- If not authorized: 403 "You can only view scans from your hospital"

---

## Testing Plan

### Step 1: Restart Backend to Pick Up Changes

```bash
# Stop any running backend processes
# Windows: Kill process on port 8000
Get-Process | Where-Object {$_.Name -match "python|uvicorn"} | Stop-Process -Force

# Or manually:
netstat -ano | findstr "8000"
# Note the PID, then: taskkill /PID {PID} /F

# Restart backend
cd C:\Users\LENOVO\Desktop\helathcare\ 2\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Step 2: Get Authentication Token

Use any valid doctor/staff credentials from your database, or create test data:

```bash
# Request
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "doctor@hospital.com",
  "password": "securepassword"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

Save the `access_token` for subsequent requests.

### Step 3: Test GET /patients/

```bash
# Request (with token from Step 2)
GET http://localhost:8000/patients/?skip=0&limit=50
Authorization: Bearer {YOUR_TOKEN}

# Expected Response
200 OK
[
  {
    "id": "550e8400-...",
    "patient_code": "PAT-20260917-0001",
    "full_name": "John Doe",
    "date_of_birth": "1985-03-15",
    "sex": "male",
    "hospital_id": "550e8400-...",
    "created_at": "2026-09-17T00:30:00",
    "updated_at": "2026-09-17T00:30:00"
  }
]
```

**Success indicators**:
- ✅ Status: 200 OK (not 405)
- ✅ Returns array of patients
- ✅ Patients are filtered by current user's hospital
- ✅ Results are paginated correctly

### Step 4: Test GET /doctor/scans/{scan_id}/image

First, get a valid scan_id from the database or from a scan upload:

```bash
# Get list of scans available for review
GET http://localhost:8000/doctor/scans/queue
Authorization: Bearer {YOUR_TOKEN}

# Find a scan_id from the response, then:
GET http://localhost:8000/doctor/scans/{scan_id}/image
Authorization: Bearer {YOUR_TOKEN}
```

**Success indicators**:
- ✅ Status: 200 OK
- ✅ Response includes `Content-Type: image/jpeg` (or png/webp)
- ✅ Response body contains binary image data
- ✅ Image can be viewed in browser

**Failure scenarios** (expected):
- ❌ 404 "Scan not found" - Scan doesn't exist in database
- ❌ 404 "Image file not found on disk" - File path invalid or file deleted
- ❌ 403 "You can only view scans from your hospital" - User from different hospital

---

## Code Verification Checklist

### ✅ GET /patients/ Endpoint
- [x] Defined with `@router.get("/")`  at line 108
- [x] Returns `List[PatientResponse]`
- [x] Accepts `skip` and `limit` query parameters
- [x] Filters by `current_user.hospital_id`
- [x] Uses `get_current_user` dependency (all authenticated users can access)
- [x] Imports: `List` is imported from `typing` (line 9)

### ✅ GET /doctor/scans/{scan_id}/image Endpoint
- [x] Defined with `@router.get("/scans/{scan_id}/image")` at line 164
- [x] Returns `FileResponse` with image bytes
- [x] Uses `require_doctor` dependency (only doctors)
- [x] Checks authorization (same hospital)
- [x] Validates file exists before serving
- [x] Sets correct Content-Type for image format
- [x] Imports: `FileResponse` is imported from `fastapi.responses` (line 2 in doctor.py)

---

## File Locations

- **GET /patients/ endpoint**: `backend/routes/patients.py:108-130`
- **GET /doctor/scans/{scan_id}/image endpoint**: `backend/routes/doctor.py:164-214`
- **Routes registered in**: `backend/main.py:41-46`

Both routers are properly included in main.py and will be active once backend restarts.

---

## Expected Outcomes After Fix

| Endpoint | Method | Before | After | Status |
|----------|--------|--------|-------|--------|
| `/patients/` | GET | 405 Method Not Allowed | 200 OK with patient list | ✅ |
| `/patients/` | POST | 201 Created | 201 Created (unchanged) | ✅ |
| `/doctor/scans/{id}/image` | GET | May not exist or 404 | 200 OK with image bytes | ✅ |
| `/doctor/scans/queue` | GET | 200 OK | 200 OK (unchanged) | ✅ |

---

## Next Steps

1. **Restart the backend process** - This is critical to reload the routes
2. **Test GET /patients/** - Verify you get 200 OK with patient list
3. **Upload a test scan** - Create test data with an image file
4. **Test GET /doctor/scans/{id}/image** - Verify you get 200 OK with image bytes
5. **Test in frontend** - Verify Patients page and Scan Review page work

If you still see errors after restarting:
- Check backend logs for Python syntax errors
- Verify database connectivity
- Check file permissions on uploaded image files
- Verify JWT token is valid and not expired
