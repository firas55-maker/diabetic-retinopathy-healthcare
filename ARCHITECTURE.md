# Healthcare Application Architecture

## System Overview

This is a **full-stack healthcare management system** for retinal scan analysis, patient management, and doctor review workflows. The architecture follows a **client-server model** with role-based access control and real-time AI-powered diagnostic assistance.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER (Browser)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────┐  ┌──────────────────────────┐                  │
│  │   React Application     │  │  Static Assets (CSS/JS)  │                  │
│  │  (SPA - Single Page)    │  │  Served from /static     │                  │
│  │                         │  │                          │                  │
│  │ • AuthContext           │  │ • React bundles          │                  │
│  │ • ProtectedRoute        │  │ • CSS stylesheets        │                  │
│  │ • Page Components       │  │ • Images                 │                  │
│  │ • API Service Layer     │  │                          │                  │
│  └────────────┬────────────┘  └──────────────────────────┘                  │
│               │                                                               │
│               │ HTTP/REST (JSON)                                             │
│               │ JWT Bearer Token                                             │
│               │ CORS enabled                                                 │
└───────────────┼───────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     API GATEWAY LAYER (FastAPI)                             │
│                      http://0.0.0.0:8000                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Route Handlers (Routers)                         │   │
│  │                                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │ auth.py      │  │ patients.py  │  │ doctor.py    │             │   │
│  │  │              │  │              │  │              │             │   │
│  │  │ • register   │  │ • CRUD       │  │ • review     │             │   │
│  │  │ • login      │  │ • lookup     │  │ • queue      │             │   │
│  │  │ • get_me     │  │ • search     │  │ • stats      │             │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │   │
│  │                                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │ scans.py     │  │ chat.py      │  │ dashboard.py │             │   │
│  │  │              │  │              │  │              │             │   │
│  │  │ • upload     │  │ • gemini     │  │ • stats      │             │   │
│  │  │ • analyze    │  │ • qa         │  │ • overview   │             │   │
│  │  │ • retrieve   │  │ • history    │  │ • trending   │             │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Middleware & Security                            │   │
│  │                                                                     │   │
│  │  • CORS (Cross-Origin Resource Sharing)                           │   │
│  │  • JWT Authentication & Authorization                             │   │
│  │  • Request/Response Validation (Pydantic)                         │   │
│  │  • Error Handling & Status Codes                                  │   │
│  │  • Static File Serving (React build)                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└───────────────┬───────────────────────────────────────────────────────────────┘
                │
    ┌───────────┴──────────────┬──────────────────┬──────────────────┐
    │                          │                  │                  │
    ▼                          ▼                  ▼                  ▼
┌─────────────┐         ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│  Business   │         │  Database   │  │  External    │  │   File       │
│   Logic     │         │   Layer     │  │    APIs      │  │  Storage     │
│   Layer     │         │             │  │              │  │              │
└─────────────┘         └─────────────┘  └──────────────┘  └──────────────┘
    │                        │                  │                  │
    │                        │                  │                  │
    ▼                        ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SERVICE & DATA LAYER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                   Auth & Security (auth_utils.py)                   │  │
│  │  • hash_password() - Bcrypt password hashing                        │  │
│  │  • verify_password() - Password validation                          │  │
│  │  • create_access_token() - JWT token generation                    │  │
│  │  • decode_token() - JWT token validation                           │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                   Data Access Layer (database.py)                   │  │
│  │  • SQLAlchemy ORM integration                                       │  │
│  │  • Session management (get_db dependency)                           │  │
│  │  • Connection pooling                                               │  │
│  │  • Transaction handling                                             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                   AI Integration (chat.py)                          │  │
│  │  • Gemini API client (httpx)                                        │  │
│  │  • PDF knowledge base retrieval                                     │  │
│  │  • Safety guardrails & content filtering                           │  │
│  │  • Chat history management                                          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                   Inference Engine (inference.py)                   │  │
│  │  • AI retinal scan grading (0-4 severity scale)                    │  │
│  │  • Confidence scoring                                               │  │
│  │  • Model inference & result caching                                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└───────────────┬───────────────────────────────────────────────────────────────┘
                │
    ┌───────────┴──────────────┬──────────────────┬──────────────────┐
    │                          │                  │                  │
    ▼                          ▼                  ▼                  ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL      │  │  Google Gemini   │  │  Filesystem  │  │  JWT Secret  │
│  Database        │  │  API             │  │  (Uploads)   │  │  (config)    │
│  :5432           │  │                  │  │              │  │              │
└──────────────────┘  └──────────────────┘  └──────────────┘  └──────────────┘
```

---

## Component Details

### **Frontend (React SPA)**

**Location:** `frontend/src/`

**Key Components:**
- **App.tsx** - Root application component with routing
- **AuthContext.tsx** - Global authentication state (JWT token, user role)
- **ProtectedRoute.tsx** - Role-based route protection
- **api.ts** - HTTP client with automatic JWT injection

**Pages (Role-based):**
```
Doctor Role:
├── DoctorDashboard.tsx
├── doctor/ScanQueue.tsx      - Review queue of pending scans
├── doctor/ScanReview.tsx     - Detailed scan analysis & grading
├── doctor/Patients.tsx       - Patient list & lookup
├── doctor/PatientDetails.tsx - Individual patient history
└── doctor/StatsPage.tsx      - Performance metrics

Technical Staff Role:
├── TechnicalStaffDashboard.tsx
├── staff/Dashboard.tsx       - Overview
├── staff/UploadScan.tsx      - Scan upload interface
├── staff/UploadHistory.tsx   - Upload history tracking
└── staff/RegisterPatient.tsx - Patient registration

Shared:
├── PatientLookup.tsx         - Patient search
├── patient/Portal.tsx        - Patient view access
└── EducationalChatWidget.tsx - AI assistant
```

**Data Flow:**
```
User Input (Form/Button)
    ↓
State Update (React State or Context)
    ↓
API Call (services/api.ts)
    ↓
HTTP Request + JWT Token
    ↓
Backend Response
    ↓
State Update & UI Render
```

---

### **Backend (FastAPI)**

**Location:** `backend/`

**Request Flow:**
```
HTTP Request
    ↓
CORS Middleware Check
    ↓
JWT Authentication (if protected route)
    ↓
Request Validation (Pydantic schemas)
    ↓
Route Handler (business logic)
    ↓
Database Query (SQLAlchemy ORM)
    ↓
Response Serialization
    ↓
HTTP Response (JSON)
```

**Route Modules:**

#### **1. auth.py** - Authentication
- `POST /auth/register` - Create new user (doctor/technical_staff)
- `POST /auth/login` - Generate JWT token
- `GET /auth/me` - Get current user info

**Dependency Chain:**
```
LoginRequest (Pydantic schema)
    ↓
Query User by email
    ↓
verify_password(request.password, user.hashed_password)
    ↓
create_access_token(email, user_id, role)
    ↓
TokenResponse with JWT
```

#### **2. patients.py** - Patient Management
- `POST /patients` - Register new patient
- `GET /patients` - List all patients (paginated)
- `GET /patients/{patient_code}` - Get patient by code
- `GET /patients/hospital/{hospital_id}` - Filter by hospital

**Queries:**
```python
# Get patient with scan history
user = db.query(User).filter(User.id == current_user.id).first()
hospital = user.hospital
patients = db.query(Patient).filter(Patient.hospital_id == hospital.id)
```

#### **3. scans.py** - Scan Upload & Analysis
- `POST /scans/upload` - Upload retinal scan image
- `GET /scans/{scan_id}` - Retrieve scan details
- `GET /scans/patient/{patient_id}` - Get patient's scans

**Processing Pipeline:**
```
Image Upload (multipart/form-data)
    ↓
File validation & storage
    ↓
inference.py - AI model inference
    ↓
Grade (0-4) + Confidence score
    ↓
Store in Scan model
    ↓
Return scan_id with results
```

#### **4. doctor.py** - Doctor Review Workflow
- `GET /doctor/queue` - Pending scans for review
- `POST /doctor/review/{scan_id}` - Submit doctor's assessment
- `GET /doctor/patients` - Reviewed patient list

**State Machine:**
```
Scan Status Flow:
PENDING_REVIEW
    ↓ (doctor reviews)
REVIEWED
    ↓ (archive if needed)
ARCHIVED
```

#### **5. chat.py** - AI Educational Assistant
- `POST /chat` - Send message to AI
- Uses Google Gemini API
- Context: PDF knowledge base + system prompts

**Integration:**
```
User Query
    ↓
Safety check (content filtering)
    ↓
Call Gemini API
    ↓
Stream/Store response
    ↓
Return to frontend
```

#### **6. dashboard.py** - Analytics & Overview
- `GET /dashboard/stats` - System statistics
- `GET /dashboard/overview` - Hospital metrics
- `GET /dashboard/trends` - Historical data

---

### **Database Layer (PostgreSQL)**

**Location:** `backend/models.py`

**Core Tables:**

```sql
hospitals
├── id (UUID, PK)
├── name (String)
├── region (String)
└── city (String)

users
├── id (UUID, PK)
├── email (String, UNIQUE)
├── hashed_password (TEXT) ← Fixed: was VARCHAR(255), now TEXT for full bcrypt hashes
├── full_name (String)
├── role (ENUM: doctor, technical_staff, admin)
├── hospital_id (FK → hospitals)
├── specialty (String, nullable)
├── created_at (DateTime)
└── updated_at (DateTime)

patients
├── id (UUID, PK)
├── patient_code (String, UNIQUE)
├── full_name (String)
├── date_of_birth (Date)
├── sex (ENUM: male, female, other)
├── phone_number (String)
├── hospital_id (FK → hospitals)
├── created_at (DateTime)
└── updated_at (DateTime)

scans
├── id (UUID, PK)
├── patient_id (FK → patients)
├── uploaded_by_id (FK → users)
├── file_path (String)
├── ai_grade (Integer: 0-4)
├── ai_confidence (Float: 0-1)
├── ai_severity (String)
├── status (ENUM: pending_review, reviewed, archived)
├── doctor_grade (Integer, nullable)
├── doctor_notes (String, nullable)
├── reviewed_at (DateTime, nullable)
├── reviewed_by_id (FK → users, nullable)
├── created_at (DateTime)
└── updated_at (DateTime)
```

**Key Relationships:**
```
Hospital (1) ─────── (N) Users
              ─────── (N) Patients

Patient (1) ──────── (N) Scans

User (1 as uploader)      (N) Scans
User (1 as reviewer) ───── (N) Scans (optional)
```

**Constraints:**
- `users.email` UNIQUE
- `patients.patient_code` UNIQUE
- `users.hospital_id` NOT NULL (FK)
- `patients.hospital_id` NOT NULL (FK)

---

### **Authentication & Security Flow**

**Registration:**
```
POST /auth/register
├── Validate email format (Pydantic EmailStr)
├── Check email uniqueness
├── hash_password(plain_password) → Bcrypt hash
├── Create User record (hashed_password stored)
└── Return JWT token (immediate login)
```

**Login:**
```
POST /auth/login
├── Query user by email
├── verify_password(request.password, user.hashed_password)
├── If match: create_access_token(email, user_id, role)
├── Return JWT with 24-hour expiry
└── Frontend stores in localStorage → adds to Authorization header
```

**Protected Routes:**
```
GET /doctor/queue
├── Extract JWT from Authorization header
├── decode_token() → TokenData(email, user_id, role)
├── Query User by user_id (refresh from DB)
├── Check role == "doctor" (via require_doctor dependency)
├── Query Scan.status == PENDING_REVIEW for user's hospital
└── Return filtered data
```

**Password Hash Details:**
```
Algorithm: Bcrypt (via passlib)
Cost factor: $2b$12$ (12 rounds)
Hash length: 60 characters
Format: $2b$12$salt$hash
Storage: TEXT column (PostgreSQL)
```

---

### **Data Flow Examples**

#### **Example 1: Scan Upload & AI Analysis**

```
FRONTEND (Staff)
    │
    ├─→ Select image file
    │
    ├─→ POST /scans/upload
    │   - multipart/form-data
    │   - patient_id
    │   - image file
    │
    ▼
BACKEND (scans.py)
    │
    ├─→ Validate file (size, type)
    │
    ├─→ Save to filesystem
    │   - /uploads/scans/{scan_id}.jpg
    │
    ├─→ Call inference.py
    │   - Load AI model
    │   - Pass image tensor
    │   - Get grade (0-4) + confidence
    │
    ├─→ Create Scan record in DB
    │   - patient_id, uploaded_by_id
    │   - ai_grade, ai_confidence
    │   - status = PENDING_REVIEW
    │   - file_path
    │
    ▼
DATABASE (PostgreSQL)
    │
    ├─→ INSERT into scans
    │   - scan_id (UUID generated)
    │   - timestamps
    │
    ▼
FRONTEND (Response)
    │
    ├─→ Display scan_id + grade
    ├─→ Show AI confidence
    └─→ Redirect to upload history

FRONTEND (Doctor)
    │
    ├─→ GET /doctor/queue
    │   - Returns pending scans
    │
    ├─→ View scan image + AI analysis
    │
    ├─→ POST /doctor/review/{scan_id}
    │   - doctor_grade (0-4)
    │   - doctor_notes
    │
    ▼
BACKEND (doctor.py)
    │
    ├─→ Update Scan record
    │   - status = REVIEWED
    │   - doctor_grade, doctor_notes
    │   - reviewed_by_id, reviewed_at
    │
    ▼
DATABASE
    │
    └─→ UPDATE scans SET status='reviewed', ...
```

#### **Example 2: Authentication Flow**

```
User enters credentials
    │
    ▼
FRONTEND (Login.tsx)
    │
    ├─→ POST /auth/login
    │   - email
    │   - password
    │
    ▼
BACKEND (auth.py)
    │
    ├─→ Query User by email
    │   db.query(User).filter(User.email == email).first()
    │
    ├─→ Verify password
    │   verify_password(request.password, user.hashed_password)
    │   └─→ Bcrypt comparison
    │
    ├─→ Generate JWT
    │   - Payload: email, user_id, role
    │   - Secret: settings.JWT_SECRET_KEY
    │   - Algorithm: HS256
    │   - Expiry: now + 24 hours
    │
    ▼
FRONTEND (AuthContext.tsx)
    │
    ├─→ Store token in localStorage
    │
    ├─→ Set authorization header
    │   Authorization: Bearer {token}
    │
    ├─→ Update AuthContext state
    │   - isAuthenticated = true
    │   - user.role = "doctor" | "technical_staff"
    │
    ▼
UI Rendering
    │
    └─→ ProtectedRoute checks role
        └─→ Render role-specific dashboard
```

---

## Key Design Patterns

### **1. Dependency Injection (FastAPI)**
```python
@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # FastAPI automatically resolves dependencies
```

### **2. Role-Based Access Control (RBAC)**
```python
@router.get("/doctor/queue")
async def get_scan_queue(
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    # Only accessible to doctor role
```

### **3. Context API (React)**
```jsx
// AuthContext provides auth state globally
<AuthProvider>
  <App />
</AuthProvider>

// Any component can access
const { user, token, logout } = useContext(AuthContext)
```

### **4. ORM Pattern (SQLAlchemy)**
```python
# Object-relational mapping
user = db.query(User).filter(User.email == email).first()
# Translates to SQL query automatically
```

---

## Deployment Architecture

**Current (Development):**
```
localhost:3000 (React dev server)
          ↓ (proxy)
localhost:8000 (FastAPI)
          ↓
PostgreSQL:5432
```

**Production (Monolithic):**
```
Frontend build (npm run build)
    ↓
Served as static files from /static
    ↓
FastAPI (main.py)
    ↓
PostgreSQL (remote/managed)
```

---

## External Integrations

### **Google Gemini API** (chat.py)
```
Request: User message + chat history
    ↓
httpx.post(https://generativelanguage.googleapis.com/...)
    ├── Model: gemini-pro
    ├── API Key: settings.GEMINI_API_KEY
    ├── Safety settings: HARM_BLOCK_THRESHOLD_BLOCKED
    │
Response: AI-generated educational content
    ↓
Store in DB for audit trail
```

---

## Summary Table

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | React 18+ | UI/UX for doctors & staff |
| Routing (FE) | React Router | Client-side navigation |
| Auth State | Context API | Global auth state |
| HTTP Client | axios/fetch | API communication |
| Backend | FastAPI | REST API server |
| Async | Uvicorn | ASGI server |
| ORM | SQLAlchemy | Database abstraction |
| Database | PostgreSQL | Persistent storage |
| Auth | JWT + Bcrypt | Secure authentication |
| AI | Google Gemini | Educational chatbot |
| Static Files | FastAPI StaticFiles | React production build |

---

## Critical Data Flows Summary

1. **Authentication** → JWT token stored locally → Attached to all requests
2. **Scan Upload** → Stored on filesystem → AI inference → DB record → Doctor review
3. **Doctor Review** → Assess AI grade → Store assessment → Update scan status
4. **Patient Query** → Hospital filtering → Multi-hospital isolation
5. **Chat** → Gemini API → Educational guidance → Audit trail

This architecture ensures **scalability, security, and clear separation of concerns** while maintaining **tight integration** between frontend and backend through well-defined REST APIs.
