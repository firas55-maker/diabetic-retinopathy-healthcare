# 🏥 Healthcare App - Complete Testing Guide

## ✅ Current Status

**Backend**: Running on `http://localhost:8000` ✓
**Frontend**: Starting on `http://localhost:3000` (compiling...)
**Database**: PostgreSQL ✓

---

## 🚀 Testing the App as a Real User

### Step 1: Open the Frontend

Once the frontend finishes compiling (should be within 1-2 minutes), open your browser and go to:

```
http://localhost:3000
```

You should see the **Login Page** of the Healthcare App.

---

### Step 2: Create Your Test Account

#### Option A: Register a New Account (via Frontend)

1. Look for a **"Register"** or **"Sign Up"** link on the login page
2. Fill in the registration form:
   - **Email**: `yourname@hospital.com` (any email)
   - **Password**: `YourPassword123` (8-72 characters)
   - **Full Name**: Your Name
   - **Role**: Select `doctor` or `technical_staff`
   - **Hospital**: Select `Central Medical Hospital` or `City Medical Center`
   - **Specialty**: (optional) Enter your specialty

3. Click **Register**
4. You should be logged in automatically and see the **Dashboard**

---

#### Option B: Use Your Existing Account

If you already registered earlier, use these credentials:

```
Email: your.email@hospital.com
Password: YourPassword123
```

---

### Step 3: Explore the Dashboard

Once logged in, you should see:

#### **For Doctors:**
- 📊 **Dashboard** - Stats, charts, scan analytics
- 👥 **Patients** - View list of patients
- 🔍 **Patient Lookup** - Search for patients
- 📸 **Scans** - View and review retinal scans
- ⚙️ **Settings** - User settings
- 🚪 **Logout** - Sign out

#### **For Technical Staff:**
- 📋 **Dashboard** - Patient management
- 👥 **Patients** - Create and manage patients
- 📸 **Scans** - Upload retinal scan images
- 🔍 **Patient Lookup** - Search patients
- 🚪 **Logout** - Sign out

---

### Step 4: Test Key Features

#### **Create a Patient**

1. Click **"Patients"** in the sidebar
2. Click **"Add New Patient"** or **"+"**
3. Fill in:
   - **Full Name**: Patient Name
   - **Date of Birth**: 1990-05-15 (format: YYYY-MM-DD)
   - **Sex**: Select male/female/other
4. Click **"Create"**
5. You should see the new patient in the list

#### **Upload a Scan**

1. Click **"Scans"** in the sidebar
2. Click **"Upload Scan"**
3. Fill in:
   - **Patient**: Select the patient you created
   - **Image**: Upload a retinal scan image (JPG/PNG)
4. Click **"Upload"**
5. The AI will analyze it and show:
   - AI Grade (0-4)
   - AI Severity
   - AI Confidence Score
   - Status (pending_review)

#### **Review a Scan** (For Doctors Only)

1. Click **"Scans"** → **"Queue"**
2. Click on a scan that needs review
3. See the patient info and AI results
4. Enter your assessment:
   - **Doctor Grade**: 0-4
   - **Notes**: Your clinical notes
5. Click **"Submit Review"**

#### **Search for a Patient**

1. Click **"Patient Lookup"** in the sidebar
2. Search by:
   - Patient Code (e.g., PAT-2026-001)
   - Patient Name
3. View patient history and previous scans

---

### Step 5: Check the Backend API

If you want to verify the backend is working, open:

```
http://localhost:8000/docs
```

This shows all API endpoints. You can:
- See all available endpoints
- Test endpoints directly
- View request/response formats

---

## 📝 Test Scenarios

### Scenario 1: Doctor Workflow
```
1. Login as a doctor
2. View dashboard with statistics
3. Search for a patient
4. View patient's scan history
5. Review a pending scan
6. Submit doctor's assessment
7. Logout
```

### Scenario 2: Technical Staff Workflow
```
1. Login as technical staff
2. Create a new patient
3. Upload a retinal scan
4. View scan analysis results
5. Search for patients
6. Logout
```

### Scenario 3: Full Patient Journey
```
1. Create a new patient
2. Upload their first scan
3. Check AI analysis
4. (Doctor) Review the scan
5. Search for patient later
6. View scan history
```

---

## 🔐 Authentication Testing

### Login Success
- Valid email + password → Redirected to dashboard ✓

### Login Failure
- Wrong password → "Invalid email or password" ✗
- Unregistered email → "Invalid email or password" ✗

### Protected Routes
- Try accessing dashboard without login → Redirected to login ✓
- Invalid/expired token → Logged out ✓

---

## 🐛 Common Issues & Solutions

### "Connection Refused" on Frontend
- **Cause**: Backend not running
- **Fix**: Make sure `http://localhost:8000` is running
- **Check**: Open `http://localhost:8000/health` in browser

### "CORS Error"
- **Cause**: Frontend/backend communication issue
- **Fix**: Both should be running on localhost
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

### "Not Authenticated"
- **Cause**: Session expired or invalid token
- **Fix**: Login again

### "Hospital not found"
- **Cause**: Using wrong hospital_id
- **Fix**: Use one of these:
  - `86aabaf3-0d6b-436d-880f-52478a0e92e2` (Central Medical Hospital)
  - `b4e21f85-632c-469c-813a-8b1ed0d76f09` (City Medical Center)

---

## 📊 Test Data

### Available Hospitals
```
1. Central Medical Hospital
   ID: 86aabaf3-0d6b-436d-880f-52478a0e92e2
   Region: North Region
   City: New York

2. City Medical Center
   ID: b4e21f85-632c-469c-813a-8b1ed0d76f09
   Region: East Region
   City: Boston
```

### Test Users (already created)
```
Email: doctor@hospital.com
Password: (from registration)

Email: doctor2@hospital.com
Password: (from registration)

Email: dr.cardiology@hospital.com
Password: (from registration)
```

---

## 🔗 Quick Links

| Component | URL | Purpose |
|-----------|-----|---------|
| Frontend | http://localhost:3000 | User interface |
| Backend | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API Health | http://localhost:8000/health | Backend status |

---

## ✨ Features to Test

- [x] User Registration
- [x] User Login
- [x] Authentication (JWT tokens)
- [x] Protected Routes
- [x] Patient Creation
- [x] Patient Search
- [x] Scan Upload
- [x] AI Analysis
- [x] Scan Review (Doctor)
- [x] User Profile
- [x] Dashboard Stats
- [x] Logout

---

## 📞 API Endpoints Reference

```
POST   /auth/register          - Register new user
POST   /auth/login             - Login
GET    /auth/me                - Get current user
POST   /patients/create        - Create patient
GET    /patients               - List patients
POST   /scans/upload           - Upload scan
GET    /scans/queue            - View scan queue
POST   /scans/{id}/review      - Review scan
GET    /scans/{id}             - Get scan details
```

---

## 🎯 Final Checklist

- [ ] Frontend loads on http://localhost:3000
- [ ] Login page displays
- [ ] Can register new account
- [ ] Can login with credentials
- [ ] Dashboard loads after login
- [ ] Can create a patient
- [ ] Can view patient list
- [ ] Can search for patients
- [ ] Can upload a scan image (if available)
- [ ] Can view scan analysis
- [ ] Can review a scan (as doctor)
- [ ] Can logout
- [ ] Backend API docs work on http://localhost:8000/docs

---

**You're all set! Start testing now! 🚀**
