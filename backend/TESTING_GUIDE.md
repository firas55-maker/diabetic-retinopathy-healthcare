# Healthcare App Testing Guide

## Base URL
```
http://localhost:8000
```

## API Documentation
Open this in your browser to see all endpoints:
```
http://localhost:8000/docs
```

---

## Step 1: Get Hospital ID

You need a valid hospital ID to register. Use one of these existing hospitals:

**Option A: Use existing hospital**
```
86aabaf3-0d6b-436d-880f-52478a0e92e2 (Central Medical Hospital)
```

**Option B: Create a new hospital**

Go to: http://localhost:8000/docs

Click on "Try it out" for any POST endpoint to test, or use Postman/curl:

```bash
curl -X POST "http://localhost:8000/hospitals" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Hospital Name",
    "region": "Your Region",
    "city": "Your City"
  }'
```

Response will give you a `hospital_id`. Copy it.

---

## Step 2: Register Your Account

### Using Postman (Recommended)

1. Open Postman
2. Create a NEW request
3. Set method to **POST**
4. Set URL to: `http://localhost:8000/auth/register`
5. Click **Body** tab
6. Select **raw** → **JSON**
7. Paste this and fill in YOUR details:

```json
{
  "email": "your.email@hospital.com",
  "password": "YourPassword123",
  "full_name": "Your Full Name",
  "role": "doctor",
  "hospital_id": "86aabaf3-0d6b-436d-880f-52478a0e92e2",
  "specialty": "Your Specialty"
}
```

8. Click **Send**

**Success Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Copy the `access_token`** - you'll need it for authenticated requests.

---

### Using curl (Command Line)

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@hospital.com",
    "password": "YourPassword123",
    "full_name": "Your Full Name",
    "role": "doctor",
    "hospital_id": "86aabaf3-0d6b-436d-880f-52478a0e92e2",
    "specialty": "Cardiology"
  }'
```

---

## Step 3: Login

If you want to login instead of register:

**Postman:**
1. POST to: `http://localhost:8000/auth/login`
2. Body (raw JSON):
```json
{
  "email": "your.email@hospital.com",
  "password": "YourPassword123"
}
```

**curl:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@hospital.com",
    "password": "YourPassword123"
  }'
```

---

## Step 4: Get Your Profile

Use the `access_token` from registration/login to make authenticated requests.

**Postman:**
1. GET to: `http://localhost:8000/auth/me`
2. Click **Headers** tab
3. Add header:
   - Key: `Authorization`
   - Value: `Bearer YOUR_ACCESS_TOKEN_HERE`
4. Click **Send**

**curl:**
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Success Response (200 OK):**
```json
{
  "id": "user-uuid-here",
  "email": "your.email@hospital.com",
  "full_name": "Your Full Name",
  "role": "doctor",
  "hospital_id": "86aabaf3-0d6b-436d-880f-52478a0e92e2",
  "specialty": "Cardiology",
  "created_at": "2026-09-16T14:54:00",
  "updated_at": "2026-09-16T14:54:00"
}
```

---

## Step 5: Test Other Endpoints

Once you have your `access_token`, you can test other endpoints:

### Create a Patient
```
POST /patients/create
Headers: Authorization: Bearer YOUR_TOKEN
Body:
{
  "full_name": "John Doe",
  "date_of_birth": "1990-05-15",
  "sex": "male"
}
```

### List Patients
```
GET /patients
Headers: Authorization: Bearer YOUR_TOKEN
```

### Upload a Scan
```
POST /scans/upload
Headers: Authorization: Bearer YOUR_TOKEN
Body: (multipart/form-data)
- file: (image file)
- patient_code: "PAT-2026-001"
```

### View Scan Queue
```
GET /scans/queue
Headers: Authorization: Bearer YOUR_TOKEN
```

### Review a Scan
```
POST /scans/{scan_id}/review
Headers: Authorization: Bearer YOUR_TOKEN
Body:
{
  "doctor_grade": 2,
  "notes": "Moderate diabetic retinopathy detected"
}
```

---

## Step 6: Using Swagger UI

The easiest way to test is using the built-in Swagger UI:

1. Open: http://localhost:8000/docs
2. Look for endpoints
3. Click on an endpoint to expand it
4. Click **"Try it out"**
5. For authenticated endpoints:
   - Click the lock icon 🔒
   - Paste your `access_token` in the dialog
6. Fill in required fields
7. Click **Execute**

---

## Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Login successful, data retrieved |
| 201 | Created | User registered, patient created |
| 400 | Bad Request | Invalid hospital_id, email already exists |
| 401 | Unauthorized | Missing/invalid token |
| 404 | Not Found | Patient/scan not found |
| 500 | Server Error | Database error |

---

## Troubleshooting

### "Email already registered" (400)
- Use a different email address

### "The specified hospital_id does not exist" (400)
- Use the correct hospital ID: `86aabaf3-0d6b-436d-880f-52478a0e92e2`
- Or create a new hospital first

### "Invalid email or password" (401)
- Check your credentials are correct
- Register first if you haven't

### "Authorization header missing" (401)
- Add header: `Authorization: Bearer YOUR_TOKEN`

### Token expired
- Login again to get a new token
- Default expiry: 24 hours

---

## Quick Test Checklist

- [ ] Register a new account
- [ ] Copy the access_token
- [ ] Login with your credentials
- [ ] Get your profile (/auth/me)
- [ ] Create a patient
- [ ] List patients
- [ ] Upload a scan (if you have an image file)
- [ ] View scan queue
- [ ] Review a scan

---

## Notes

- All timestamps are in UTC
- Passwords must be 8-72 characters
- Email must be valid
- Hospital ID must exist
- Role must be: "doctor" or "technical_staff"
- Sex must be: "male", "female", or "other"
