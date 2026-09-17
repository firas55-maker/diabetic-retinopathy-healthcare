# Healthcare Frontend - React Setup Guide

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx                          # Main routing setup
│   ├── index.tsx                        # Entry point
│   ├── index.css                        # Global styles
│   ├── context/
│   │   └── AuthContext.tsx             # Auth state management & JWT parsing
│   ├── services/
│   │   └── api.ts                      # API client with all endpoints
│   ├── components/
│   │   ├── ProtectedRoute.tsx          # Protected & public route wrappers
│   │   └── Sidebar.tsx                 # Navigation sidebar
│   ├── pages/
│   │   ├── Login.tsx                   # Login page
│   │   ├── PatientLookup.tsx           # Public patient lookup
│   │   ├── PatientLookup.css           # Patient lookup styles
│   │   ├── Unauthorized.tsx            # 403 page
│   │   ├── DoctorDashboard.tsx         # Doctor main dashboard
│   │   ├── TechnicalStaffDashboard.tsx # Staff main dashboard
│   │   ├── doctor/
│   │   │   ├── ScanQueue.tsx           # Pending scans queue
│   │   │   ├── MyPatients.tsx          # Patient history
│   │   │   └── StatsPage.tsx           # Advanced analytics
│   │   └── staff/
│   │       ├── RegisterPatient.tsx     # Patient registration form
│   │       ├── UploadScan.tsx          # Scan upload with AI results
│   │       └── MyUploads.tsx           # Upload history & status
│   ├── package.json
│   └── .env.example
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This will install:
- **react-router-dom**: Client-side routing with protected routes
- **axios**: HTTP client for API communication
- **recharts**: Charts & data visualization
- **date-fns**: Date formatting utilities
- **typescript**: Type safety

### 2. Configure Environment

Create `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000
```

For production:
```env
REACT_APP_API_URL=https://api.healthcare.com
```

### 3. Run Development Server

```bash
npm start
```

App will open at `http://localhost:3000`

---

## Authentication Flow

### 1. JWT Token Storage & Parsing

The `AuthContext` handles:
- **Login**: Sends email/password, receives JWT token
- **Token Parsing**: Decodes JWT payload to extract:
  - `email`: User email
  - `role`: User role (doctor, technical_staff, admin)
  - `user_id`: User UUID
- **Storage**: Saves token & claims to localStorage
- **Logout**: Clears all data

**JWT Payload Structure:**
```json
{
  "email": "doctor@hospital.com",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "doctor",
  "exp": 1696161600
}
```

### 2. Protected Routes

`ProtectedRoute` component:
- Checks if user is authenticated (has token & role)
- Optionally checks if role matches required role(s)
- Redirects to login if not authenticated
- Redirects to /unauthorized if role doesn't match

```tsx
<Route
  path="/doctor/dashboard"
  element={
    <ProtectedRoute requiredRole="doctor">
      <DoctorDashboard />
    </ProtectedRoute>
  }
/>
```

### 3. Public Routes

`PublicRoute` component:
- Redirects authenticated users away from login page
- Redirects to appropriate dashboard based on role

```tsx
<Route
  path="/login"
  element={
    <PublicRoute>
      <Login />
    </PublicRoute>
  }
/>
```

---

## Role-Based Routing

### Landing Page Flow

```
/ → PatientLookup (public)
  ↓
User chooses:
├─ Patient Lookup (no auth)
│  └─ Enter patient_code + DOB
│     └─ View own scans & doctor assessments
│
└─ Staff Login
   └─ /login
      ├─ Doctor Login
      │  └─ /doctor/dashboard
      │     ├─ Dashboard (home)
      │     ├─ /doctor/queue (scan queue)
      │     ├─ /doctor/patients (my patients)
      │     └─ /doctor/stats (analytics)
      │
      └─ Technical Staff Login
         └─ /staff/dashboard
            ├─ Dashboard (home)
            ├─ /staff/register-patient (new patient)
            ├─ /staff/upload-scan (upload image)
            └─ /staff/my-uploads (upload history)
```

---

## Page Components

### Public Pages

#### PatientLookup (`/`)
- **Access**: No authentication required
- **Security**: Date-of-birth verification
- **Returns**: Patient's own scans with doctor assessments
- **Features**:
  - Search by patient code + DOB
  - View scan history
  - See doctor grades & clinical notes
  - Link to staff login

#### Login (`/login`)
- **Access**: Public (redirects if already logged in)
- **Features**:
  - Email/password authentication
  - JWT token generation
  - Automatic role detection
  - Demo credentials display

### Doctor Pages

#### DoctorDashboard (`/doctor/dashboard`)
- **Access**: Doctor only
- **Features**:
  - Total patients count
  - Reviewed scans statistics
  - DR prevalence percentage
  - Age group breakdown (bar chart)
  - Monthly scan volume trend (line chart)
  - DR prevalence pie chart
  - Age distribution pie chart

#### ScanQueue (`/doctor/queue`)
- **Access**: Doctor only
- **Features**:
  - List all pending_review scans
  - Filter by region/hospital
  - AI grade & confidence display
  - Click to review individual scans
  - Table with patient info

#### MyPatients (`/doctor/patients`)
- **Access**: Doctor only
- **Features**:
  - All reviewed patients list
  - Patient demographics
  - Scan count per patient
  - Latest scan date
  - Latest grades (AI vs Doctor)

#### StatsPage (`/doctor/stats`)
- **Access**: Doctor only
- **Features**:
  - Personal stats vs hospital average toggle
  - All dashboard charts
  - Comparison metrics
  - Age group analysis
  - Monthly trends

### Technical Staff Pages

#### TechnicalStaffDashboard (`/staff/dashboard`)
- **Access**: Technical staff only
- **Features**:
  - Total uploads count
  - Pending review count
  - Reviewed count
  - Quick action buttons
  - Recent uploads table

#### RegisterPatient (`/staff/register-patient`)
- **Access**: Technical staff only
- **Features**:
  - Patient registration form
  - Auto-generated patient_code
  - Success message with code
  - Birth date validation
  - Sex selection

#### UploadScan (`/staff/upload-scan`)
- **Access**: Technical staff only
- **Features**:
  - File upload input
  - Patient code lookup
  - Image type validation (JPEG, PNG, WebP)
  - AI analysis results display
  - Grade, severity, confidence
  - Status indicator

#### MyUploads (`/staff/my-uploads`)
- **Access**: Technical staff only
- **Features**:
  - Upload history table
  - AI grade display
  - Doctor grade (once reviewed)
  - Status indicators
  - Upload/review timestamps
  - Quick stats cards

---

## API Integration

### Authentication API

```typescript
// Login
const response = await api.login({ email, password });
// Returns: { access_token, token_type, expires_in }

// Get current user
const user = await api.getCurrentUser();
```

### Patient API

```typescript
// Create patient
const patient = await api.createPatient({
  full_name,
  date_of_birth,
  sex
});
// Returns: { patient_code, id, full_name }

// Public lookup (no auth)
const patientData = await api.patientLookup(patientCode, dateOfBirth);
```

### Scan API

```typescript
// Upload scan
const result = await api.uploadScan(patientCode, file);
// Returns: { scan_id, ai_grade, ai_confidence, ai_severity, status }

// Get my uploads (staff)
const uploads = await api.getMyScans();

// Get scan queue (doctor)
const queue = await api.getScanQueue();

// Submit review (doctor)
await api.submitScanReview(scanId, doctorGrade, notes);
```

### Dashboard API

```typescript
// Personal dashboard stats
const stats = await api.getDashboardStats();

// Hospital-wide stats
const hospitalStats = await api.getHospitalStats();
```

---

## Styling Architecture

### Global Styles (`index.css`)

**Components:**
- `.dashboard-container` - Main layout with sidebar
- `.sidebar` - Navigation sidebar
- `.main-content` - Content area
- `.card` - Content cards
- `.form-group` - Form fields
- `.btn`, `.btn-primary`, `.btn-secondary` - Buttons
- `.badge`, `.badge-pending`, `.badge-reviewed` - Status badges
- `.grid-2`, `.grid-3` - Responsive grid layouts
- `.stat-card` - Statistics cards
- `.table` - Data tables
- `.alert`, `.alert-info`, `.alert-error` - Alerts
- `.spinner` - Loading animation

**Theme:**
- Primary gradient: #667eea → #764ba2
- Text: #2c3e50
- Borders: #e0e0e0
- Background: #f5f5f5

### Page-Specific Styles

**PatientLookup.css:**
- `.lookup-container` - Full-page layout
- `.lookup-card` - Search card
- `.patient-info` - Info display
- `.scan-item` - Scan card
- `.grade`, `.status` - Badge styling

---

## Features Implemented

✅ **Role-Based Routing**
- Doctor dashboard with analytics
- Technical staff dashboard with uploads
- Public patient lookup with DOB verification
- Automatic role detection from JWT

✅ **Authentication**
- JWT token storage & parsing
- Protected routes with role checking
- Login page with error handling
- Logout functionality

✅ **Doctor Features**
- Scan queue with pending reviews
- Patient history tracking
- Advanced statistics dashboard
- Charts: line, bar, pie
- Age group breakdowns
- Monthly trends

✅ **Technical Staff Features**
- Patient registration with auto-generated codes
- Scan upload with file validation
- AI results display
- Upload history with status tracking

✅ **Public Features**
- Patient lookup (no auth)
- DOB verification for security
- Scan history display
- Doctor assessments visible

✅ **UI/UX**
- Responsive design (mobile-friendly)
- Sidebar navigation
- Quick action buttons
- Data tables with sorting
- Charts with Recharts
- Status badges
- Loading states
- Error handling

---

## Development Workflow

### Adding a New Page

1. Create file: `src/pages/PageName.tsx`
2. Export React component
3. Add route in `App.tsx`
4. Protect with `<ProtectedRoute>` if needed

### Adding an API Endpoint

1. Add method to `src/services/api.ts`
2. Use in component with `await api.methodName()`
3. Handle errors with try/catch

### Styling New Components

- Use classes from `index.css` for consistency
- Follow BEM naming: `.component-name`, `.component-name__element`
- Use CSS Grid for layouts
- Mobile-first responsive design

---

## Environment Variables

### Development
```env
REACT_APP_API_URL=http://localhost:8000
```

### Production
```env
REACT_APP_API_URL=https://api.healthcare.com
REACT_APP_ENV=production
```

### Available Variables
- `REACT_APP_API_URL` - Backend API base URL
- `REACT_APP_ENV` - Environment (development/production)

---

## Deployment

### Build for Production

```bash
npm run build
```

Creates optimized build in `build/` directory.

### Deploy to Hosting

**Vercel:**
```bash
npm install -g vercel
vercel
```

**Netlify:**
```bash
npm run build
netlify deploy --prod --dir=build
```

**Docker:**
```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Troubleshooting

### Token not persisting after refresh
- Check localStorage in DevTools
- Verify `localStorage.getItem('token')` in AuthContext

### Routes redirecting to login
- Check JWT token format (should be 3 parts separated by .)
- Verify token expiration
- Check role claim in decoded token

### API requests failing with 401
- Token might be expired
- Call logout and login again
- Check `Authorization: Bearer <token>` header

### Charts not rendering
- Ensure data is passed correctly to Recharts components
- Verify data structure matches chart requirements
- Check browser console for errors

### Sidebar not showing
- Check if inside `<ProtectedRoute>`
- Verify role is set in AuthContext
- Check CSS for display issues

---

## Next Steps

1. ✅ Start development server: `npm start`
2. ✅ Test authentication with demo credentials
3. ✅ Verify role-based routing works
4. ✅ Test each role's dashboard
5. ✅ Integrate with backend API
6. ✅ Deploy to production

---

## Support

For issues or questions:
1. Check browser console for errors
2. Verify backend API is running
3. Check network requests in DevTools
4. Review component props and state
5. Consult TypeScript type definitions

Happy coding! 🚀
