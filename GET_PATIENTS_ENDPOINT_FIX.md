# GET /patients/ Endpoint Fix

## Problem
Frontend called `GET /patients/?skip=0&limit=50` to fetch the doctor's patient list, but received **405 Method Not Allowed** error.

## Root Cause
The `/patients/` endpoint only had a **POST method** (for creating patients). There was **no GET method** to list patients.

**Before**: Only these endpoints existed
```
POST   /patients/                 → Create patient (technical_staff only)
GET    /patients/{patient_code}   → Get one patient by code
POST   /scans/
GET    /scans/mine
GET    /scans/{scan_id}
GET    /patient-lookup/{patient_code}
```

**Missing**: `GET /patients/` for listing paginated patients

## Solution
Added `GET /patients/` endpoint in `backend/routes/patients.py`

### Endpoint Specification

```python
@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[PatientResponse]:
```

**Method**: GET  
**Path**: `/patients/`  
**Auth**: Requires authentication (any authenticated user)  
**Query Parameters**:
- `skip` (int, default=0): Records to skip (pagination offset)
- `limit` (int, default=50, max=200): Max records to return

**Response**: Array of `PatientResponse` objects
```json
[
  {
    "id": "uuid",
    "patient_code": "PAT-20260917-0001",
    "full_name": "Jane Smith",
    "date_of_birth": "1990-05-15",
    "sex": "female",
    "hospital_id": "uuid",
    "created_at": "2026-09-17T01:00:00",
    "updated_at": "2026-09-17T01:00:00"
  }
]
```

### Implementation Details

✅ **Filtering by Hospital**: Returns only patients from current user's hospital  
✅ **Pagination**: Supports skip/limit for efficient data loading  
✅ **Sorting**: Orders by created_at descending (newest first)  
✅ **Security**: Requires authentication via `get_current_user` dependency  
✅ **Response Format**: Returns list of `PatientResponse` objects matching schema

### Frontend Integration

Now the following call succeeds:

```typescript
// frontend/src/pages/doctor/Patients.tsx
const data = await api.getPatients(skip=0, limit=50);
// Returns: Array<PatientResponse>

// frontend/src/services/api.ts
async getPatients(skip: number = 0, limit: number = 50): Promise<any> {
  const response = await this.client.get('/patients/', {
    params: { skip, limit },
  });
  return response.data;
}
```

## Updated Endpoint Summary

Now all patient endpoints are complete:

| Endpoint | Method | Purpose | Auth | Role |
|----------|--------|---------|------|------|
| `/patients/` | **GET** | **List patients (paginated)** | ✅ Yes | Any |
| `/patients/` | POST | Create patient | ✅ Yes | technical_staff |
| `/patients/{patient_code}` | GET | Get patient by code | ✅ Yes | Any |
| `/scans/` | POST | Upload scan | ✅ Yes | technical_staff |
| `/scans/mine` | GET | Get my scans | ✅ Yes | technical_staff |
| `/scans/{scan_id}` | GET | Get scan by ID | ✅ Yes | Any |
| `/doctor/scans/queue` | GET | Get review queue | ✅ Yes | doctor |
| `/doctor/scans/{scan_id}` | GET | Get scan detail | ✅ Yes | doctor |
| `/doctor/scans/{scan_id}/image` | GET | Get scan image file | ✅ Yes | doctor |
| `/doctor/scans/{scan_id}/review` | POST | Submit review | ✅ Yes | doctor |

## Files Modified

- `backend/routes/patients.py` - Added `list_patients()` function with `@router.get("/")` decorator

## Testing

```bash
# Test with curl (after getting JWT token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/patients/?skip=0&limit=10"

# Expected response: 200 OK with array of patients
```

Frontend call now works:
```typescript
const patients = await api.getPatients(0, 50);
// ✅ Returns array of PatientResponse objects
// ✅ Doctor Patients page displays patient list
```
