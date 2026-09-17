# Role-Check Code Reference - Exact Locations & Implementation

## 📋 Table of Contents
1. [JWT Role Extraction](#1-jwt-role-extraction-authcontexttsx)
2. [Route Protection](#2-route-protection-apptsx)
3. [Access Control Enforcement](#3-access-control-enforcement-protectedroutetsx)
4. [Navigation Filtering](#4-navigation-filtering-appshelltsx)
5. [Console Debug Logs](#5-console-debug-logs)

---

## 1. JWT Role Extraction (AuthContext.tsx)

**File:** `frontend/src/context/AuthContext.tsx`

### Code: Role Extraction from JWT

```typescript
const login = (newToken: string) => {
  try {
    const parts = newToken.split('.');
    if (parts.length !== 3) throw new Error('Invalid token format');

    // 🔑 JWT DECODED - Role extracted here
    const decoded = JSON.parse(atob(parts[1]));

    // Validate required fields exist
    if (!decoded.role || !decoded.email || !decoded.user_id) {
      throw new Error('Missing required JWT fields: role, email, or user_id');
    }

    // Validate role is recognized
    const validRoles = ['doctor', 'technical_staff', 'admin', 'patient'];
    if (!validRoles.includes(decoded.role)) {
      console.warn(`[AuthContext] Invalid role in token: '${decoded.role}'. Valid roles: ${validRoles.join(', ')}`);
    }

    // 💾 Store role in React state
    setRole(decoded.role);

    // 💾 Persist role to localStorage
    localStorage.setItem('role', decoded.role);
    localStorage.setItem('email', decoded.email);
    localStorage.setItem('userId', decoded.user_id);

    console.log(`[AuthContext] Login successful - Role: ${decoded.role}, Email: ${decoded.email}`);
  } catch (error) {
    console.error('[AuthContext] Failed to parse token:', error);
    setRole(null);
  }
};
```

### What Role Values Can Be

```typescript
decoded.role can be one of:
- "doctor"
- "technical_staff"
- "admin"
- "patient"

Any other value:
- Logs warning
- But still sets the role (validation happens later in ProtectedRoute)
```

### Example JWT Payload

```json
{
  "user_id": "usr_12345",
  "email": "doctor@hospital.com",
  "role": "doctor",
  "exp": 1726521958,
  "iat": 1726518358
}
```

→ Decoded and stored as:
```typescript
{
  role: "doctor",
  email: "doctor@hospital.com",
  userId: "usr_12345",
  token: "eyJhbGc...",
  isAuthenticated: true
}
```

---

## 2. Route Protection (App.tsx)

**File:** `frontend/src/App.tsx`

### Code: Doctor Routes with Role Guard

```typescript
{/* Doctor Routes */}
<Route
  path="/doctor/dashboard"
  element={
    <ProtectedRoute requiredRole="doctor">
      <DoctorDashboard />
    </ProtectedRoute>
  }
/>
<Route
  path="/doctor/queue"
  element={
    <ProtectedRoute requiredRole="doctor">
      <ScanQueue />
    </ProtectedRoute>
  }
/>
<Route
  path="/doctor/patients"
  element={
    <ProtectedRoute requiredRole="doctor">
      <DoctorPatients />
    </ProtectedRoute>
  }
/>
<Route
  path="/doctor/patients/:patientId"
  element={
    <ProtectedRoute requiredRole="doctor">
      <PatientDetails />
    </ProtectedRoute>
  }
/>
<Route
  path="/doctor/scan/:scanId"
  element={
    <ProtectedRoute requiredRole="doctor">
      <ScanReview />
    </ProtectedRoute>
  }
/>
```

**Key:** `requiredRole="doctor"` = only users with role `"doctor"` can access

### Code: Technical Staff Routes with Role Guard

```typescript
{/* Technical Staff Routes */}
<Route
  path="/staff/dashboard"
  element={
    <ProtectedRoute requiredRole="technical_staff">
      <StaffDashboard />
    </ProtectedRoute>
  }
/>
<Route
  path="/staff/register-patient"
  element={
    <ProtectedRoute requiredRole="technical_staff">
      <RegisterPatient />
    </ProtectedRoute>
  }
/>
<Route
  path="/staff/upload-scan"
  element={
    <ProtectedRoute requiredRole="technical_staff">
      <UploadScan />
    </ProtectedRoute>
  }
/>
<Route
  path="/staff/uploads"
  element={
    <ProtectedRoute requiredRole="technical_staff">
      <UploadHistory />
    </ProtectedRoute>
  }
/>
```

**Key:** `requiredRole="technical_staff"` = only users with role `"technical_staff"` can access

### Code: Public/Login Routes (No Role Required)

```typescript
{/* Public Routes */}
<Route
  path="/login"
  element={
    <PublicRoute>
      <Login />
    </PublicRoute>
  }
/>
<Route path="/patient-lookup" element={<PatientLookup />} />
<Route path="/patient/:patientCode" element={<PatientPortal />} />
<Route path="/unauthorized" element={<Unauthorized />} />
```

---

## 3. Access Control Enforcement (ProtectedRoute.tsx)

**File:** `frontend/src/components/ProtectedRoute.tsx`

### Code: Full Role Verification Logic

```typescript
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
}) => {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  // ========== STEP 1: Check Authentication ==========
  if (!isAuthenticated) {
    console.warn(`[ProtectedRoute] Unauthenticated access attempt to ${location.pathname}`);
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // ========== STEP 2: Check Role Requirement ==========
  if (requiredRole) {
    // Convert single role to array (allows multiple acceptable roles)
    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];

    // ========== STEP 3: Log Verification Attempt ==========
    console.log(
      `[ProtectedRoute] Role verification: path=${location.pathname}, userRole=${role}, required=${roles.join(', ')}, authorized=${role && roles.includes(role)}`
    );

    // ========== STEP 4: ⚡ CRITICAL ROLE CHECK ⚡ ==========
    if (!role || !roles.includes(role)) {
      // Role mismatch - access DENIED
      console.error(
        `[ProtectedRoute] UNAUTHORIZED ACCESS: User with role '${role}' attempted to access ${location.pathname} (required: ${roles.join(', ')})`
      );
      return <Navigate to="/unauthorized" replace />;
    }
  }

  // ========== STEP 5: Access Granted ==========
  console.debug(`[ProtectedRoute] Access granted to ${location.pathname} for role: ${role}`);
  return <>{children}</>;
};
```

### Logic Breakdown

```
Check 1: Authentication
├─ if (!isAuthenticated)
│  └─ Redirect to /login
└─ Continue

Check 2: Role Guard Defined
├─ if (requiredRole is defined)
│  └─ Check role matches
└─ else
   └─ Allow access (no role requirement)

Check 3: Role Comparison
├─ roles = Convert requiredRole to array
├─ if (user.role NOT in roles)
│  ├─ Log error
│  ├─ Redirect to /unauthorized
│  └─ DENY ACCESS ❌
└─ else
   ├─ Log success
   └─ GRANT ACCESS ✅ → Render children
```

### Example Scenario: Doctor Accesses `/staff/upload-scan`

```typescript
// Route definition in App.tsx
<Route
  path="/staff/upload-scan"
  element={
    <ProtectedRoute requiredRole="technical_staff">
      <UploadScan />
    </ProtectedRoute>
  }
/>

// User state
{
  isAuthenticated: true,
  role: "doctor",        // ← Problem: needs "technical_staff"
}

// ProtectedRoute execution
if (!isAuthenticated)  // false - user is authenticated ✓
  // Skip

if (requiredRole)      // true - requires "technical_staff"
  roles = ["technical_staff"]
  
  console.log(
    `[ProtectedRoute] Role verification: 
     path=/staff/upload-scan, 
     userRole=doctor, 
     required=technical_staff, 
     authorized=false`
  )

  if (!role || !roles.includes(role))  // true - "doctor" not in ["technical_staff"]
    console.error(
      `[ProtectedRoute] UNAUTHORIZED ACCESS: 
       User with role 'doctor' attempted to access 
       /staff/upload-scan (required: technical_staff)`
    )
    return <Navigate to="/unauthorized" replace />  // ❌ DENY

// Result: User redirected to /unauthorized page
```

---

## 4. Navigation Filtering (AppShell.tsx)

**File:** `frontend/src/components/AppShell.tsx`

### Code: Doctor Navigation Items

```typescript
const getDoctorNavItems = () => [
  { label: 'Dashboard', path: '/doctor/dashboard', icon: '📊' },
  { label: 'Scan Queue', path: '/doctor/queue', icon: '⏳' },
  { label: 'My Patients', path: '/doctor/patients', icon: '👥' },
];
```

### Code: Staff Navigation Items

```typescript
const getStaffNavItems = () => [
  { label: 'Dashboard', path: '/staff/dashboard', icon: '📊' },
  { label: 'Register Patient', path: '/staff/register-patient', icon: '➕' },
  { label: 'Upload Scan', path: '/staff/upload-scan', icon: '📤' },
  { label: 'Upload History', path: '/staff/uploads', icon: '📋' },
];
```

### Code: Role-Based Navigation Selection

```typescript
export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, email, role } = useAuth();

  // ========== LOG CURRENT ROLE ==========
  React.useEffect(() => {
    console.log('[AppShell] Current role:', role);
  }, [role]);

  // ========== SELECT NAV ITEMS BASED ON ROLE ==========
  const navItems = role === 'doctor'
    ? getDoctorNavItems()          // 3 items for doctor
    : role === 'technical_staff'
    ? getStaffNavItems()            // 4 items for staff
    : [];                           // 0 items for unknown role

  const roleLabel = role === 'doctor'
    ? 'Doctor'
    : role === 'technical_staff'
    ? 'Technical Staff'
    : 'User';

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>RetinalCare</h2>
          <p>Screening Platform</p>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section">
            <div className="nav-section-title">Navigation</div>
            {navItems.map((item) => (
              <div key={item.path} className="nav-item">
                <a
                  href={item.path}
                  className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    navigate(item.path);
                  }}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </a>
              </div>
            ))}
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="user-info-small">
            <p><strong>{roleLabel}</strong></p>
            <p>{email}</p>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            Sign Out
          </button>
        </div>
      </aside>
    </div>
  );
};
```

### Navigation Rendering

```typescript
// If role = "doctor"
navItems = getDoctorNavItems()
→ Render:
   <Dashboard → /doctor/dashboard
   <Scan Queue → /doctor/queue
   <My Patients → /doctor/patients

// If role = "technical_staff"
navItems = getStaffNavItems()
→ Render:
   <Dashboard → /staff/dashboard
   <Register Patient → /staff/register-patient
   <Upload Scan → /staff/upload-scan
   <Upload History → /staff/uploads

// If role = null or unknown
navItems = []
→ Render: (empty - no navigation items)
```

---

## 5. Console Debug Logs

### When Doctor Logs In

```javascript
// Browser Console Output:
[AuthContext] Login successful - Role: doctor, Email: doctor@hospital.com
[AppShell] Current role: doctor
[ProtectedRoute] Role verification: path=/doctor/dashboard, userRole=doctor, required=doctor, authorized=true
[ProtectedRoute] Access granted to /doctor/dashboard for role: doctor
```

### When Doctor Tries to Access `/staff/upload-scan`

```javascript
// Browser Console Output:
[ProtectedRoute] Role verification: path=/staff/upload-scan, userRole=doctor, required=technical_staff, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'doctor' attempted to access /staff/upload-scan (required: technical_staff)
// Page redirects to /unauthorized
```

### When Staff Logs In

```javascript
// Browser Console Output:
[AuthContext] Login successful - Role: technical_staff, Email: staff@hospital.com
[AppShell] Current role: technical_staff
[ProtectedRoute] Role verification: path=/staff/dashboard, userRole=technical_staff, required=technical_staff, authorized=true
[ProtectedRoute] Access granted to /staff/dashboard for role: technical_staff
```

### When Staff Tries to Access `/doctor/queue`

```javascript
// Browser Console Output:
[ProtectedRoute] Role verification: path=/doctor/queue, userRole=technical_staff, required=doctor, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'technical_staff' attempted to access /doctor/queue (required: doctor)
// Page redirects to /unauthorized
```

### When Unauthenticated User Tries to Access Protected Route

```javascript
// Browser Console Output:
[ProtectedRoute] Unauthenticated access attempt to /doctor/dashboard
// Page redirects to /login
```

---

## 🔐 Security Checks Summary

| Check | Location | Code | Enforced At |
|-------|----------|------|-------------|
| **Role Extracted** | AuthContext.tsx | `const role = decoded.role` | JWT parse time |
| **Role Validated** | AuthContext.tsx | `validRoles.includes(role)` | Login time |
| **Role Checked** | ProtectedRoute.tsx | `roles.includes(role)` | Route access time |
| **Navigation Filtered** | AppShell.tsx | `role === 'doctor' ? getDoctorNavItems() : ...` | Render time |
| **URL Direct Access** | ProtectedRoute.tsx | Redirect to `/unauthorized` | Route load time |

---

## 🧪 How to Verify Role-Check Logic

### In Browser DevTools Console (F12):

```javascript
// Check stored role
localStorage.getItem('role')
// Output: "doctor" or "technical_staff"

// Check if user is authenticated
localStorage.getItem('token')
// Output: "eyJhbGc..." or null if not logged in

// Monitor role changes in real-time
// Check Console tab for "[AppShell] Current role: ..."
// Check for "[ProtectedRoute] UNAUTHORIZED ACCESS" errors
```

### Test Steps:

1. **Login as Doctor**
   ```
   Email: doctor@hospital.com
   Password: password
   ```
   - Expected: Redirects to /doctor/dashboard
   - Console: `[AuthContext] Login successful - Role: doctor`

2. **Try to Access Staff Page**
   ```
   Navigate to: http://localhost/staff/upload-scan
   ```
   - Expected: Redirected to /unauthorized
   - Console: `[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'doctor'...`

3. **Check Navigation Menu**
   - Expected: Only shows Dashboard, Scan Queue, My Patients
   - NOT showing: Register Patient, Upload Scan, Upload History

4. **Logout**
   - Expected: Clears role, token from localStorage
   - Next visit to /doctor/dashboard → redirects to /login

5. **Login as Staff**
   ```
   Email: staff@hospital.com
   Password: password
   ```
   - Expected: Redirects to /staff/dashboard
   - Console: `[AuthContext] Login successful - Role: technical_staff`

6. **Verify Staff Cannot Access Doctor Routes**
   ```
   Navigate to: http://localhost/doctor/queue
   ```
   - Expected: Redirected to /unauthorized
   - Console: `[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'technical_staff'...`

---

## Summary

**3-Layer Role-Based Access Control:**

1. **JWT Layer:** Role extracted from token, validated against whitelist
2. **Route Layer:** Each route guards with `<ProtectedRoute requiredRole="...">`
3. **UI Layer:** Navigation menu shows only role-appropriate items

**Result:**
- Doctor cannot see staff navigation items
- Doctor cannot access `/staff/*` routes directly (redirected to /unauthorized)
- Technical staff cannot see doctor navigation items
- Technical staff cannot access `/doctor/*` routes directly (redirected to /unauthorized)
- All access attempts logged to browser console for debugging

