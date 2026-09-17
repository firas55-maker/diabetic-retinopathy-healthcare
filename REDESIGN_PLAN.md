# Frontend Redesign Implementation Plan

## Phase 1: Foundation (Design System + App Shell)
- [ ] Design system CSS variables and base styles
- [ ] Global typography and spacing system
- [ ] Reusable component library (Button, Card, Badge, etc.)
- [ ] Professional AppShell with Sidebar
- [ ] TopBar with user info and notifications
- [ ] Responsive layout system

## Phase 2: Doctor Application
- [ ] Dashboard - KPI cards, activity charts, recent cases
- [ ] Patients page - Professional table, search/filter
- [ ] Patient details - Scan history, patient info
- [ ] Scan queue - Pending reviews, status filters
- [ ] AI Review interface - Image viewer, analysis, assessment form

## Phase 3: Technical Staff Application
- [ ] Dashboard - Operational metrics
- [ ] Patient registration - Form with generated code
- [ ] Scan upload - Multi-step workflow
- [ ] Upload history - Track uploads

## Phase 4: Patient Portal
- [ ] Patient dashboard - Latest result, history
- [ ] Educational assistant UI (backend dependency)

---

## API Endpoints to Verify

### Authentication
- ✅ POST /auth/register
- ✅ POST /auth/login
- ✅ GET /auth/me

### Doctor Endpoints
- ✅ GET /dashboard/stats - Doctor statistics
- ✅ GET /scans/queue - Pending reviews
- ✅ GET /patients - Doctor's patients
- ⚠️ GET /patients/{id} - Patient details (verify if exists)
- ⚠️ GET /scans/{id} - Scan details with AI analysis
- ⚠️ POST /scans/{id}/review - Submit doctor assessment

### Technical Staff Endpoints
- ✅ POST /patients/create - Register patient
- ✅ POST /scans/upload - Upload retinal image
- ⚠️ GET /uploads/my-uploads - Upload history (verify)
- ⚠️ GET /dashboard/stats - Staff dashboard stats (verify)

---

## Critical Questions Before Implementation

1. Do we have endpoints to fetch:
   - Individual patient details (age, DOB, hospital, registration date)?
   - Individual scan details with AI analysis (grade, confidence, heatmap)?
   - Doctor's patient list with metadata?

2. For the AI Review page:
   - How does the existing CV model provide results?
   - Is there a Grad-CAM/heatmap visualization?
   - Does the backend expose these, or do we process them client-side?

3. For upload workflow:
   - Does the backend immediately return AI results, or are they async?
   - Do we poll for results, or does the API return them immediately?

4. For patient portal:
   - Should patients access via patient code + password?
   - Or via patient-specific authentication?

---

## Status: READY TO BUILD

Once these are answered, I will:

1. Build the design system completely
2. Create reusable component library
3. Implement AppShell with proper navigation
4. Build Doctor Dashboard with real API data
5. Incrementally add all other pages
6. Test each phase with actual backend

**NO fake data will be used - only real API data or designed empty states.**
