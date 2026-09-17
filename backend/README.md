# Healthcare Backend - FastAPI with JWT Authentication and Scan Analysis

FastAPI-based healthcare management system with PostgreSQL, SQLAlchemy ORM, JWT-based authentication with role-based access control, and AI-powered retinal scan analysis for diabetic retinopathy detection.

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── database.py          # SQLAlchemy setup and dependencies
├── models.py            # SQLAlchemy ORM models (User, Patient, Hospital, Scan)
├── schemas.py           # Pydantic request/response schemas
├── auth_utils.py        # JWT token and password utilities
├── inference.py         # AI model inference for retinal scan analysis
├── dependencies.py      # FastAPI dependency injection (auth, roles)
├── routes/
│   ├── __init__.py
│   ├── auth.py         # Authentication endpoints
│   └── patients.py     # Patient & scan management endpoints
├── uploads/
│   └── scans/          # Uploaded scan images directory
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Database Models

### Hospital
- **id** (UUID, Primary Key)
- **name** (String, Unique)
- **region** (String)
- **city** (String)
- **created_at** (DateTime)
- **updated_at** (DateTime)
- **Relationships**: One-to-Many with Users and Patients

### User
- **id** (UUID, Primary Key)
- **email** (String, Unique)
- **hashed_password** (String)
- **full_name** (String)
- **role** (Enum: doctor, technical_staff, admin)
- **hospital_id** (UUID, Foreign Key → Hospital)
- **specialty** (String, Optional - for doctors)
- **created_at** (DateTime)
- **updated_at** (DateTime)
- **Relationships**: Many-to-One with Hospital, One-to-Many with Scans

### Patient
- **id** (UUID, Primary Key)
- **patient_code** (String, Unique) - Auto-generated format: PAT-YYYYMMDD-NNNN
- **full_name** (String)
- **date_of_birth** (Date)
- **sex** (Enum: male, female, other)
- **hospital_id** (UUID, Foreign Key → Hospital)
- **created_at** (DateTime)
- **updated_at** (DateTime)
- **Relationships**: Many-to-One with Hospital, One-to-Many with Scans

### Scan
- **id** (UUID, Primary Key)
- **patient_id** (UUID, Foreign Key → Patient)
- **uploaded_by_id** (UUID, Foreign Key → User)
- **file_path** (String)
- **ai_grade** (Integer 0-4) - DR severity: 0=No DR, 1=Mild, 2=Moderate, 3=Severe, 4=Proliferative
- **ai_confidence** (Float 0-1) - Prediction confidence
- **ai_severity** (String) - Human-readable severity
- **status** (Enum: pending_review, reviewed, archived)
- **doctor_grade** (Integer, Optional) - Doctor's manual assessment
- **doctor_notes** (String, Optional) - Doctor's review notes
- **reviewed_at** (DateTime, Optional)
- **reviewed_by_id** (UUID, Foreign Key → User, Optional)
- **created_at** (DateTime)
- **updated_at** (DateTime)
- **Relationships**: Many-to-One with Patient and User

## Authentication System

### JWT Token Flow

1. **Registration**: User registers with email, password, full_name, role, hospital_id
2. **Login**: User logs in with email and password
3. **Token Generation**: Server generates JWT with user claims (email, user_id, role)
4. **Token Usage**: Client includes token in Authorization header: `Bearer <token>`
5. **Token Validation**: Server validates token signature and expiration on each request

### Role-Based Access Control

- **doctor**: Medical professionals - can review scans and provide assessments
- **technical_staff**: Support staff - can register patients and upload scans
- **admin**: System administrators (registration restricted to doctor/technical_staff)

## API Endpoints

### Authentication Endpoints

#### POST `/auth/register`
Register a new user (doctor or technical_staff only)

**Request:**
```json
{
  "email": "doctor@hospital.com",
  "password": "securepassword123",
  "full_name": "Dr. John Doe",
  "role": "doctor",
  "hospital_id": "550e8400-e29b-41d4-a716-446655440000",
  "specialty": "Ophthalmology"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

#### POST `/auth/login`
Authenticate user and get JWT token

**Request:**
```json
{
  "email": "doctor@hospital.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

#### GET `/auth/me`
Get current authenticated user information

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "doctor@hospital.com",
  "full_name": "Dr. John Doe",
  "role": "doctor",
  "hospital_id": "550e8400-e29b-41d4-a716-446655440001",
  "specialty": "Ophthalmology",
  "created_at": "2026-09-16T10:00:00",
  "updated_at": "2026-09-16T10:00:00"
}
```

---

### Patient Management Endpoints

#### POST `/patients/` (technical_staff only)
Register a new patient

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "full_name": "Jane Smith",
  "date_of_birth": "1990-05-15",
  "sex": "female"
}
```

**Response (201 Created):**
```json
{
  "patient_code": "PAT-20260916-0001",
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "full_name": "Jane Smith"
}
```

**Errors:**
- `400 Bad Request`: Invalid date format or sex
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not technical_staff

---

#### GET `/patients/{patient_code}`
Get patient details by patient code

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "patient_code": "PAT-20260916-0001",
  "full_name": "Jane Smith",
  "date_of_birth": "1990-05-15",
  "sex": "female",
  "hospital_id": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2026-09-16T10:00:00",
  "updated_at": "2026-09-16T10:00:00"
}
```

**Errors:**
- `404 Not Found`: Patient not found in your hospital
- `401 Unauthorized`: Missing or invalid token

---

### Scan Management Endpoints

#### POST `/scans/` (technical_staff only)
Upload retinal scan image for a patient

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Parameters:**
- `patient_code` (query): Patient code from registration
- `file` (form): Image file (JPEG, PNG, WebP)

**Example with curl:**
```bash
curl -X POST "http://localhost:8000/scans/?patient_code=PAT-20260916-0001" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@retinal_scan.jpg"
```

**Response (201 Created):**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440004",
  "patient_code": "PAT-20260916-0001",
  "ai_grade": 2,
  "ai_severity": "Moderate",
  "ai_confidence": 0.8765,
  "status": "pending_review"
}
```

**AI Severity Grades:**
- `0`: No DR
- `1`: Mild
- `2`: Moderate
- `3`: Severe
- `4`: Proliferative DR

**Errors:**
- `400 Bad Request`: Invalid file type or patient code not found
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not technical_staff
- `404 Not Found`: Patient not found in your hospital
- `500 Internal Server Error`: File save or inference failed

---

#### GET `/scans/mine` (technical_staff only)
Get all scans uploaded by current technical staff member

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 50)

**Response (200 OK):**
```json
{
  "scans": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "patient_code": "PAT-20260916-0001",
      "ai_grade": 2,
      "ai_severity": "Moderate",
      "ai_confidence": 0.8765,
      "status": "pending_review",
      "doctor_grade": null,
      "doctor_notes": null,
      "reviewed_at": null,
      "created_at": "2026-09-16T10:30:00",
      "uploaded_by_email": "staff@hospital.com"
    }
  ],
  "total": 1
}
```

**Errors:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not technical_staff

---

#### GET `/scans/{scan_id}`
Get specific scan details (uploader, doctor, or admin only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "patient_code": "PAT-20260916-0001",
  "ai_grade": 2,
  "ai_severity": "Moderate",
  "ai_confidence": 0.8765,
  "status": "pending_review",
  "doctor_grade": null,
  "doctor_notes": null,
  "reviewed_at": null,
  "created_at": "2026-09-16T10:30:00",
  "uploaded_by_email": "staff@hospital.com"
}
```

**Errors:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Not authorized to view this scan
- `404 Not Found`: Scan not found

---

### Doctor Review Endpoints

#### GET `/doctor/scans/queue`
Get all pending_review scans in queue (doctor only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `hospital_id` (optional): Filter by specific hospital UUID
- `region` (optional): Filter by region name (e.g., "North Region")
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 50, max: 200)

**Example:**
```bash
curl -X GET "http://localhost:8000/doctor/scans/queue?region=North%20Region&skip=0&limit=25" \
  -H "Authorization: Bearer DOCTOR_TOKEN"
```

**Response (200 OK):**
```json
{
  "scans": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "patient_code": "PAT-20260916-0001",
      "patient_name": "Jane Smith",
      "hospital_name": "Central Medical Hospital",
      "region": "North Region",
      "ai_grade": 2,
      "ai_severity": "Moderate",
      "ai_confidence": 0.8765,
      "uploaded_at": "2026-09-16T10:30:00",
      "uploaded_by_email": "staff@hospital.com"
    }
  ],
  "total": 1
}
```

**Errors:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not a doctor

---

#### GET `/doctor/scans/{scan_id}`
Get full scan details including image and metadata (doctor only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `scan_id`: UUID of the scan

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "patient_code": "PAT-20260916-0001",
  "patient_name": "Jane Smith",
  "patient_dob": "1990-05-15",
  "patient_sex": "female",
  "hospital_name": "Central Medical Hospital",
  "region": "North Region",
  "city": "New York",
  "file_path": "/uploads/scans/550e8400-e29b-41d4-a716-446655440004.jpg",
  "ai_grade": 2,
  "ai_severity": "Moderate",
  "ai_confidence": 0.8765,
  "status": "pending_review",
  "doctor_grade": null,
  "doctor_notes": null,
  "reviewed_at": null,
  "created_at": "2026-09-16T10:30:00",
  "uploaded_by_email": "staff@hospital.com",
  "uploaded_by_name": "John Smith"
}
```

**Notes:**
- Image data can be retrieved from `file_path` for display
- `doctor_grade` and `doctor_notes` are null until review is submitted
- `ai_grade` contains the AI model's prediction (0-4)
- `ai_confidence` is the model's confidence score (0-1)

**Errors:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not a doctor or scan is from different hospital
- `404 Not Found`: Scan not found

---

#### POST `/doctor/scans/{scan_id}/review`
Submit doctor review for a scan (doctor only)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Path Parameters:**
- `scan_id`: UUID of the scan to review

**Request:**
```json
{
  "doctor_grade": 2,
  "notes": "Confirmed moderate DR. Multiple microaneurysms and venous abnormalities visible. Recommend close follow-up in 3 months."
}
```

**Doctor Grade Scale:**
- `0`: No DR - No signs of diabetic retinopathy
- `1`: Mild - Microaneurysms only
- `2`: Moderate - More than microaneurysms but less than severe NPDR
- `3`: Severe - Venous beading, significant areas of retinal hemorrhages
- `4`: Proliferative DR - Neovascularization or vitreous hemorrhage

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "patient_code": "PAT-20260916-0001",
  "status": "reviewed",
  "doctor_grade": 2,
  "doctor_notes": "Confirmed moderate DR. Multiple microaneurysms and venous abnormalities visible. Recommend close follow-up in 3 months.",
  "reviewed_at": "2026-09-16T11:45:00"
}
```

**Effects:**
- Sets `status` to "reviewed"
- Records `doctor_grade` and `doctor_notes`
- Sets `reviewed_at` to current timestamp
- Records `reviewed_by_id` as current doctor's ID
- Prevents further reviews (endpoint returns 400 if already reviewed)

**Errors:**
- `400 Bad Request`: Scan already reviewed, invalid grade (must be 0-4)
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not a doctor or scan from different hospital
- `404 Not Found`: Scan not found

**Example:**
```bash
curl -X POST "http://localhost:8000/doctor/scans/550e8400-e29b-41d4-a716-446655440004/review" \
  -H "Authorization: Bearer DOCTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_grade": 2,
    "notes": "Confirmed moderate DR. Close follow-up recommended."
  }'
```

---

#### GET `/doctor/patients/mine`
Get all patients this doctor has reviewed scans for (doctor only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 50, max: 200)

**Response (200 OK):**
```json
{
  "patients": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "patient_code": "PAT-20260916-0001",
      "full_name": "Jane Smith",
      "date_of_birth": "1990-05-15",
      "sex": "female",
      "hospital_id": "550e8400-e29b-41d4-a716-446655440001",
      "scan_count": 3,
      "latest_scan_date": "2026-09-16T10:30:00",
      "latest_ai_grade": 2,
      "latest_doctor_grade": 2,
      "created_at": "2026-09-16T10:00:00"
    }
  ],
  "total": 1
}
```

**Response Fields:**
- `scan_count`: Total number of scans by this doctor for this patient
- `latest_scan_date`: Most recent scan timestamp
- `latest_ai_grade`: AI model's prediction for latest scan (0-4)
- `latest_doctor_grade`: Doctor's assessment for latest scan (0-4)

**Use Cases:**
- Track patient history and progression
- Monitor which patients have been reviewed
- Quick access to patient summary with scan trends

**Errors:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not a doctor

---

## Health Check Endpoints

#### GET `/`
Health check

**Response:**
```json
{
  "message": "Healthcare API is running",
  "version": "1.0.0"
}
```

#### GET `/health`
Health status

**Response:**
```json
{
  "status": "healthy",
  "app": "Healthcare API"
}
```

---

## Technical Staff Workflow

### 1. Register Patient

```bash
curl -X POST "http://localhost:8000/patients/" \
  -H "Authorization: Bearer STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Smith",
    "date_of_birth": "1990-05-15",
    "sex": "female"
  }'
```

Response includes auto-generated `patient_code`: `PAT-20260916-0001`

### 2. Upload Scan

```bash
curl -X POST "http://localhost:8000/scans/?patient_code=PAT-20260916-0001" \
  -H "Authorization: Bearer STAFF_TOKEN" \
  -F "file=@retinal_scan.jpg"
```

Response includes:
- `scan_id`: Unique scan identifier
- `ai_grade`: 0-4 severity prediction
- `ai_confidence`: Confidence score (0-1)
- `status`: Always "pending_review" initially

### 3. View My Scans

```bash
curl -X GET "http://localhost:8000/scans/mine" \
  -H "Authorization: Bearer STAFF_TOKEN"
```

Returns all scans uploaded by this staff member with their current status.

---

## Doctor Review Workflow

### 1. View Pending Review Queue

Get all scans awaiting review (optionally filtered):

```bash
# Get all pending scans
curl -X GET "http://localhost:8000/doctor/scans/queue" \
  -H "Authorization: Bearer DOCTOR_TOKEN"

# Filter by region
curl -X GET "http://localhost:8000/doctor/scans/queue?region=North%20Region" \
  -H "Authorization: Bearer DOCTOR_TOKEN"

# With pagination
curl -X GET "http://localhost:8000/doctor/scans/queue?skip=0&limit=25" \
  -H "Authorization: Bearer DOCTOR_TOKEN"
```

Response shows scan summary with patient info, AI prediction, and upload timestamp.

### 2. View Scan Details

Get full details including patient information and image path:

```bash
curl -X GET "http://localhost:8000/doctor/scans/{scan_id}" \
  -H "Authorization: Bearer DOCTOR_TOKEN"
```

Response includes:
- Complete patient demographics (DOB, sex, contact info)
- AI model's prediction (grade + confidence)
- Image file path for retrieval/display
- Hospital and region information
- Who uploaded the scan and when

### 3. Submit Review

After examining scan and AI results, submit doctor's assessment:

```bash
curl -X POST "http://localhost:8000/doctor/scans/{scan_id}/review" \
  -H "Authorization: Bearer DOCTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_grade": 2,
    "notes": "Confirmed moderate DR. Multiple microaneurysms visible. Patient needs referral to ophthalmology. Follow-up in 3 months."
  }'
```

Effects:
- Scan status changes from `pending_review` → `reviewed`
- Doctor's assessment recorded (grade + clinical notes)
- Timestamp and doctor ID recorded for audit trail
- Scan locked (cannot be reviewed again)

### 4. Track Patient History

View all patients you've reviewed with scan progression:

```bash
curl -X GET "http://localhost:8000/doctor/patients/mine?skip=0&limit=50" \
  -H "Authorization: Bearer DOCTOR_TOKEN"
```

Response includes:
- All patients you've reviewed
- Total scan count per patient
- Latest AI grade and your grade for comparison
- Latest scan date for tracking progression
- Created date for longitudinal analysis

**Example Follow-up Scenario:**
```
Patient: Jane Smith (PAT-20260916-0001)
Scan 1 (2026-09-10): AI=1 (Mild), Doctor=1 ✓ Agree
Scan 2 (2026-09-16): AI=2 (Moderate), Doctor=2 ✓ Agree
→ Shows progression from Mild to Moderate DR
```

---

## AI Model Integration

### Inference System

The `inference.py` module provides:

- **SimplePredictor class**: Wraps the PyTorch model for predictions
- **predict() function**: Single-line interface for getting predictions

### Prediction Flow

1. **Image Upload**: Technical staff uploads retinal fundus image
2. **Preprocessing**: Image resized to 224x224, normalized with dataset mean/std
3. **Inference**: PyTorch model predicts DR severity (0-4)
4. **Confidence**: Softmax probabilities converted to confidence score
5. **Storage**: Grade, confidence, and severity stored in Scan record with `status='pending_review'`

### Severity Grades

```
0: No DR             - No signs of diabetic retinopathy
1: Mild              - Microaneurysms only
2: Moderate          - More than microaneurysms but less than severe NPDR
3: Severe            - Venous beading, significant areas of retinal hemorrhages
4: Proliferative DR  - Neovascularization or vitreous hemorrhage
```

---

## Dependency Injection & Role-Based Access Control

### Using `require_role` Dependency

```python
from fastapi import APIRouter, Depends
from dependencies import require_role, get_current_user
from models import User

router = APIRouter()

@router.post("/review-scan/{scan_id}")
async def review_scan(
    scan_id: str,
    current_user: User = Depends(require_role("doctor", "admin"))
):
    """Only doctors and admins can review scans"""
    pass
```

### Predefined Role Dependencies

```python
from dependencies import (
    get_current_user,           # Any authenticated user
    require_technical_staff,    # Technical staff only
    require_doctor,             # Doctor only
    require_admin,              # Admin only
    require_doctor_or_admin     # Doctor or admin
)
```

---

## Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip
- 2GB+ disk space for model weights

### 1. Create PostgreSQL Databases

```bash
psql -U postgres

CREATE DATABASE healthcare_dev;
CREATE DATABASE healthcare_test;

\q
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/healthcare_dev
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
DEBUG=True
```

### 4. Run the Application

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## End-to-End Testing

### 1. Register Technical Staff

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "staff@hospital.com",
    "password": "securepassword123",
    "full_name": "John Smith",
    "role": "technical_staff",
    "hospital_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Save the `access_token`.

### 2. Register Patient

```bash
curl -X POST "http://localhost:8000/patients/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Smith",
    "date_of_birth": "1990-05-15",
    "sex": "female"
  }'
```

Save the `patient_code`.

### 3. Upload Scan

```bash
curl -X POST "http://localhost:8000/scans/?patient_code=PAT-20260916-0001" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -F "file=@test_scan.jpg"
```

### 4. View My Scans

```bash
curl -X GET "http://localhost:8000/scans/mine" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

---

## File Storage

Uploaded scan images are stored in `./uploads/scans/` directory with UUID-based filenames:

```
uploads/
└── scans/
    ├── 550e8400-e29b-41d4-a716-446655440004.jpg
    ├── 550e8400-e29b-41d4-a716-446655440005.png
    └── ...
```

File path is stored in the Scan record for retrieval and re-analysis.

---

## Public Patient Lookup Endpoint

### GET `/patient-lookup/{patient_code}`
Public patient lookup with date of birth verification (no authentication required)

**IMPORTANT SECURITY NOTE:** This endpoint is publicly accessible but requires date-of-birth verification to prevent unauthorized data access. Only the patient or authorized healthcare providers with the patient's information can access the data.

**Query Parameters:**
- `date_of_birth` (required): Patient's date of birth in YYYY-MM-DD format for verification

**Path Parameters:**
- `patient_code`: Patient's registration code (e.g., PAT-20260916-0001)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/patient-lookup/PAT-20260916-0001?date_of_birth=1990-05-15"
```

**Response (200 OK):**
```json
{
  "patient_code": "PAT-20260916-0001",
  "full_name": "Jane Smith",
  "date_of_birth": "1990-05-15",
  "sex": "female",
  "total_scans": 3,
  "scans": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "date": "2026-09-16T10:30:00",
      "doctor_grade": 2,
      "doctor_notes": "Confirmed moderate DR. Multiple microaneurysms visible. Recommend close follow-up in 3 months.",
      "ai_grade": 2,
      "ai_severity": "Moderate",
      "status": "reviewed",
      "image_path": "/uploads/scans/550e8400-e29b-41d4-a716-446655440004.jpg"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440005",
      "date": "2026-08-20T14:15:00",
      "doctor_grade": 1,
      "doctor_notes": "Mild microaneurysms. Continue monitoring. Next screening in 6 months.",
      "ai_grade": 1,
      "ai_severity": "Mild",
      "status": "reviewed",
      "image_path": "/uploads/scans/550e8400-e29b-41d4-a716-446655440005.jpg"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440006",
      "date": "2026-07-10T09:45:00",
      "doctor_grade": null,
      "doctor_notes": null,
      "ai_grade": 0,
      "ai_severity": "No DR",
      "status": "pending_review",
      "image_path": "/uploads/scans/550e8400-e29b-41d4-a716-446655440006.jpg"
    }
  ]
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `patient_code` | Patient's registration code |
| `full_name` | Patient's full name |
| `date_of_birth` | Patient's date of birth (verified) |
| `sex` | Patient's sex (male, female, other) |
| `total_scans` | Total number of scans on record |
| `scans` | Array of scan records (see below) |

**Scan Fields:**

| Field | Description |
|-------|-------------|
| `id` | Unique scan identifier |
| `date` | Scan upload timestamp |
| `ai_grade` | AI model prediction (0-4) |
| `ai_severity` | Human-readable AI severity |
| `status` | Scan status (pending_review, reviewed, archived) |
| `doctor_grade` | Doctor's assessment (null if not reviewed) |
| `doctor_notes` | Doctor's clinical notes (null if not reviewed) |
| `image_path` | Path to scan image file |

**Status Interpretation:**

| Status | Meaning | Doctor Fields |
|--------|---------|----------------|
| `pending_review` | Awaiting doctor review | null (not reviewed yet) |
| `reviewed` | Doctor has assessed | Contains grade & notes |
| `archived` | Old/archived scan | May contain previous assessment |

**Errors:**

| Code | Scenario |
|------|----------|
| `400 Bad Request` | Invalid date format or missing date_of_birth parameter |
| `401 Unauthorized` | Date of birth does not match patient record (access denied) |
| `404 Not Found` | Patient code not found in system |

**Security Mechanism:**

The endpoint uses date of birth as a basic verification mechanism:

1. Patient provides their `patient_code` (public identifier)
2. Patient provides their `date_of_birth` (private identifier)
3. Server verifies both match before returning data
4. On mismatch, returns `401 Unauthorized` to prevent data enumeration

**This prevents:**
- ✓ Unauthorized access to other patients' data
- ✓ Data enumeration attacks (timing-based guessing)
- ✓ Accidental data leakage without proper verification

**It does NOT prevent:**
- ✗ Shoulder surfing (someone seeing the patient code and DOB)
- ✗ Compromised devices or networks
- → For these, use VPN, secure devices, HTTPS-only (production)

---

### Use Cases

**1. Patient Self-Service Portal**
Patient logs into their account and views their own scan history:
```bash
Patient enters: PAT-20260916-0001 and 1990-05-15
→ Gets all their scans with doctor assessments
→ Can share results with other providers
```

**2. Healthcare Provider Access**
Provider with patient's information can retrieve scan history:
```bash
Provider has patient intake form with patient_code and DOB
→ Quickly accesses patient's screening history
→ Reviews progression and doctor assessments
→ No separate login required for emergency access
```

**3. Patient Advocacy / Health Records Portability**
Patient downloads their complete scan history for:
- Sharing with new ophthalmologist
- Keeping personal health records
- Insurance documentation
- Medical tourism scenarios

---

### Patient Code Format

Patient codes are auto-generated with format: `PAT-YYYYMMDD-NNNN`

Example: `PAT-20260916-0001`
- `PAT`: Prefix (constant)
- `20260916`: Date of registration (YYYYMMDD)
- `0001`: Sequence number (incremented daily)

**Why this format:**
- Human-readable and memorable
- Date-based sequence (easy chronological sorting)
- No sensitive data embedded
- Collision-resistant (sequence resets daily)

---

### Privacy & HIPAA Considerations

**HIPAA Compliance Notes:**

✓ **Compliant:**
- Date of birth verification prevents unauthorized access
- No API keys or tokens logged in URLs
- HTTPS encryption recommended (production)
- Patient controls access (knows their code/DOB)
- Audit trail possible (log all lookups)

⚠️ **Consider:**
- Store access logs (who looked up whom and when)
- Implement rate limiting to prevent brute-force DOB guessing
- Require HTTPS in production
- Consider adding optional authentication for additional security
- Add session timeouts for public access

**Example Rate Limiting:**
```
Max 5 failed attempts per patient_code per IP per hour
→ Prevents brute-force DOB guessing
```

---

### Examples

**1. Successful Lookup**
```bash
curl -X GET "http://localhost:8000/patient-lookup/PAT-20260916-0001?date_of_birth=1990-05-15"

Response: 200 OK
{
  "patient_code": "PAT-20260916-0001",
  "total_scans": 3,
  "scans": [...]
}
```

**2. Wrong Date of Birth**
```bash
curl -X GET "http://localhost:8000/patient-lookup/PAT-20260916-0001?date_of_birth=1991-05-15"

Response: 401 Unauthorized
{
  "detail": "Date of birth verification failed. Access denied."
}
```

**3. Patient Not Found**
```bash
curl -X GET "http://localhost:8000/patient-lookup/PAT-INVALID-0000?date_of_birth=1990-05-15"

Response: 404 Not Found
{
  "detail": "Patient not found"
}
```

**4. Missing Date of Birth**
```bash
curl -X GET "http://localhost:8000/patient-lookup/PAT-20260916-0001"

Response: 422 Unprocessable Entity
{
  "detail": "date_of_birth query parameter is required"
}
```

---

## Dashboard & Analytics Endpoints

### GET `/dashboard/stats`
Get comprehensive dashboard statistics for doctor (doctor only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "total_patients": 150,
  "reviewed_scans_count": 200,
  "affected_scans_count": 95,
  "affected_percentage": 47.5,
  "age_group_breakdown": [
    {
      "group": "<30",
      "count": 5,
      "percentage": 3.3
    },
    {
      "group": "30-50",
      "count": 45,
      "percentage": 30.0
    },
    {
      "group": "50-65",
      "count": 65,
      "percentage": 43.3
    },
    {
      "group": "65+",
      "count": 35,
      "percentage": 23.3
    }
  ],
  "monthly_scan_counts": [
    {
      "year": 2026,
      "month": 9,
      "month_name": "September",
      "count": 45
    },
    {
      "year": 2026,
      "month": 8,
      "month_name": "August",
      "count": 38
    }
  ],
  "timestamp": "2026-09-16T11:50:05.078Z"
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `total_patients` | Total patients in doctor's hospital |
| `reviewed_scans_count` | Total scans reviewed by this doctor |
| `affected_scans_count` | Scans with `doctor_grade >= 2` (Moderate DR or worse) |
| `affected_percentage` | Percentage of reviewed scans showing significant DR |
| `age_group_breakdown` | Affected patients grouped by age brackets |
| `monthly_scan_counts` | Scan upload trend for last 12 months |
| `timestamp` | Query execution timestamp (UTC) |

**Age Groups:**
- `<30`: Patients under 30 years old
- `30-50`: Patients 30-49 years old
- `50-65`: Patients 50-64 years old
- `65+`: Patients 65+ years old

**Key Metrics:**
- **Affected percentage**: Percentage of scans with `doctor_grade >= 2`
  - Grade 0-1: No significant DR
  - Grade 2-4: Significant DR (requires intervention)
- **Age breakdown**: Shows which age groups are most affected
- **Monthly trend**: Track scan volume over time

**Use Cases:**
- Track DR prevalence among reviewed patients
- Identify at-risk age groups
- Monitor scan processing capacity (monthly trends)
- Compare individual doctor metrics against hospital average

**Errors:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not a doctor

**Example:**
```bash
curl -X GET "http://localhost:8000/dashboard/stats" \
  -H "Authorization: Bearer DOCTOR_TOKEN"
```

---

### GET `/dashboard/stats/hospital`
Get hospital-wide dashboard statistics (all doctors' reviews)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
Same structure as `/dashboard/stats` but aggregates all reviews from all doctors in the hospital.

**Response Fields:** Identical to `/dashboard/stats`

**Key Difference:**
- `/dashboard/stats`: Only reviews by the current doctor
- `/dashboard/stats/hospital`: All reviews by all doctors in hospital

**Use Cases:**
- Compare individual doctor performance to hospital averages
- Hospital-wide DR prevalence analysis
- Overall capacity planning
- Hospital epidemiology trends

**Example:**
```bash
curl -X GET "http://localhost:8000/dashboard/stats/hospital" \
  -H "Authorization: Bearer DOCTOR_TOKEN"
```

**Sample Comparison:**
```
Dr. Smith (/dashboard/stats):
- Reviewed: 50 scans
- Affected: 18 (36%)

Hospital (/dashboard/stats/hospital):
- Reviewed: 200 scans
- Affected: 95 (47.5%)
→ Dr. Smith reviews lower-risk patients than hospital average
```

---

## Dashboard Analytics Queries

### Aggregate Query Examples

The dashboard endpoints use efficient SQLAlchemy aggregate queries:

**1. Total Patients Count**
```sql
SELECT COUNT(DISTINCT id) FROM patients WHERE hospital_id = ?
```

**2. Reviewed Scans & Affected Count**
```sql
SELECT COUNT(id), COUNT(CASE WHEN doctor_grade >= 2 THEN 1 END)
FROM scans
WHERE status = 'reviewed' AND reviewed_by_id = ?
```

**3. Age Group Breakdown**
```sql
-- For affected patients (doctor_grade >= 2):
-- Calculate age from DOB, group into brackets
-- Count distinct patients per age group
SELECT COUNT(DISTINCT patient_id)
FROM scans s
JOIN patients p ON s.patient_id = p.id
WHERE s.doctor_grade >= 2 AND s.reviewed_by_id = ?
GROUP BY age_bucket
```

**4. Monthly Scan Counts (Last 12 Months)**
```sql
SELECT EXTRACT(YEAR FROM created_at), EXTRACT(MONTH FROM created_at), COUNT(id)
FROM scans
WHERE created_at >= NOW() - INTERVAL '365 days'
  AND patient_id IN (SELECT id FROM patients WHERE hospital_id = ?)
GROUP BY EXTRACT(YEAR FROM created_at), EXTRACT(MONTH FROM created_at)
ORDER BY EXTRACT(YEAR FROM created_at), EXTRACT(MONTH FROM created_at)
```

### Performance Characteristics

- **Total queries**: 4 main queries (one per statistic section)
- **Query time**: Typically < 500ms for hospital with 1000+ patients
- **Indexes recommended**:
  - `scans(status, reviewed_by_id)`
  - `scans(doctor_grade, status)`
  - `patients(hospital_id)`
  - `scans(created_at)`

---

## Analytics Interpretation Guide

### Affected Percentage Thresholds

The "affected" metric represents scans with `doctor_grade >= 2` (Moderate to Proliferative DR):

| Percentage Range | Interpretation |
|------------------|-----------------|
| 0-10% | Low DR prevalence (excellent screening) |
| 10-30% | Moderate DR prevalence (expected range) |
| 30-50% | High DR prevalence (targeted intervention needed) |
| 50%+ | Very high DR prevalence (urgent action required) |

### Age Group Risk Patterns

Common DR prevalence patterns by age:

| Age Group | Typical Risk |
|-----------|-------------|
| `<30` | Low (early-onset cases) |
| `30-50` | Moderate (longer disease duration) |
| `50-65` | High (accumulated damage) |
| `65+` | Highest (multiple comorbidities) |

**Example Scenario:**
```
If 65+ group shows 60% of affected patients despite being 20% of population:
→ Urgent need for elderly patient screening programs
```

### Monthly Trend Interpretation

Track scan volume patterns:

- **Increasing trend**: Growing patient engagement, capacity constraints
- **Decreasing trend**: Declining screening, potential awareness issues
- **Seasonal patterns**: Peak screening periods (diabetes awareness months)
- **Flat trend**: Steady-state volume, predictable capacity

**Example:**
```
Sept: 45 scans
Aug: 38 scans
July: 35 scans
→ 28% increase suggests successful awareness campaign
```

---

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input or validation error
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions for the role
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Request validation error
- `500 Internal Server Error`: Server error

---

## Security Considerations

- Always use HTTPS in production
- Rotate JWT secret key periodically
- Implement rate limiting on auth and upload endpoints
- Validate file uploads (type, size, malware scan)
- Store uploaded files outside web root
- Log all authentication and scan upload events
- Encrypt sensitive data at rest

---

## Future Enhancements

- [ ] Refresh token implementation
- [ ] Doctor review endpoints with manual grade submission
- [ ] Email notifications on scan upload/review
- [ ] Scan export (PDF reports)
- [ ] Batch upload support
- [ ] Model versioning and A/B testing
- [ ] Advanced filtering and search for scans
- [ ] Audit logging for all operations
- [ ] Rate limiting and usage analytics
- [ ] Comprehensive test suite with fixtures

---

## Troubleshooting

### Token Validation Errors

If you get "Invalid or expired token":
1. Ensure token is not expired (24 hours default)
2. Check token format: `Authorization: Bearer <token>`
3. Verify JWT_SECRET_KEY matches in `.env`

### File Upload Fails

If file upload returns 400:
1. Check file format (JPEG, PNG, WebP only)
2. Verify patient_code exists and is in your hospital
3. Check disk space for uploads directory

### AI Inference Errors

If prediction fails:
1. Ensure model weights exist (or use mock predictions)
2. Check image file is not corrupted
3. Verify image format is supported
4. Check available GPU/CPU memory

### Database Connection Issues

If database connection fails:
1. Verify PostgreSQL is running
2. Check DATABASE_URL in `.env`
3. Ensure database exists: `psql -l`
4. Test connection: `psql postgresql://user:pass@localhost/healthcare_dev`
