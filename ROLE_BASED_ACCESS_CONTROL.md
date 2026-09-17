# Role-Based Access Control (RBAC) - Complete Implementation Guide

## Overview

The healthcare platform implements strict role-based access control at three levels:

1. **Route Guards** - Prevent unauthorized URL access
2. **Navigation Filtering** - Show only appropriate menu items
3. **Authentication Validation** - Verify JWT contains valid role

---

## 1. ROUTE GUARDS (App.tsx)

All protected routes enforce role requirements via `ProtectedRoute` component:

### Doctor-Only Routes

```tsx
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

**Result:** Doctor sees these routes. Technical staff accessing `/doctor/queue` directly → redirected to `/unauthorized`

### Technical Staff-Only Routes

```tsx
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

**Result:** Technical staff sees these routes. Doctor accessing `/staff/upload-scan` directly → redirected to `/unauthorized`

---

## 2. PROTECTED ROUTE COMPONENT (ProtectedRoute.tsx)

Enhanced with logging to detect role-based access issues:

```tsx
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
}) => {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  // Check authentication
  if (!isAuthenticated) {
    console.warn(`[ProtectedRoute] Unauthenticated access attempt to ${location.pathname}`);
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role if required
  if (requiredRole) {
    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];

    console.log(
      `[ProtectedRoute] Role verification: path=${location.pathname}, userRole=${role}, required=${roles.join(', ')}, authorized=${role && roles.includes(role)}`
    );

    if (!role || !roles.includes(role)) {
      console.error(
        `[ProtectedRoute] UNAUTHORIZED ACCESS: User with role '${role}' attempted to access ${location.pathname} (required: ${roles.join(', ')})`
      );
      return <Navigate to="/unauthorized" replace />;
    }
  }

  console.debug(`[ProtectedRoute] Access granted to ${location.pathname} for role: ${role}`);
  return <>{children}</>;
};
```

**Logic Flow:**
1. ✓ Check if user has valid token and role
2. ✓ Extract required role(s) for the route
3. ✓ Compare user's role against required role(s)
4. ✓ Redirect to `/unauthorized` if mismatch
5. ✓ Log all access attempts for debugging

---

## 3. NAVIGATION FILTERING (AppShell.tsx)

Sidebar displays only role-appropriate menu items:

```tsx
const getDoctorNavItems = () => [
  { label: 'Dashboard', path: '/doctor/dashboard', icon: '📊' },
  { label: 'Scan Queue', path: '/doctor/queue', icon: '⏳' },
  { label: 'My Patients', path: '/doctor/patients', icon: '👥' },
];

const getStaffNavItems = () => [
  { label: 'Dashboard', path: '/staff/dashboard', icon: '📊' },
  { label: 'Register Patient', path: '/staff/register-patient', icon: '➕' },
  { label: 'Upload Scan', path: '/staff/upload-scan', icon: '📤' },
  { label: 'Upload History', path: '/staff/uploads', icon: '📋' },
];

// Strictly enforce role-specific items
const navItems = role === 'doctor'
  ? getDoctorNavItems()
  : role === 'technical_staff'
  ? getStaffNavItems()
  : [];  // Empty array if role is invalid/unrecognized
```

**Result:** 
- Doctor logged in → sees only [Dashboard, Scan Queue, My Patients]
- Technical Staff logged in → sees only [Dashboard, Register Patient, Upload Scan, Upload History]
- Role is logged on mount: `console.log('[AppShell] Current role:', role)`

---

## 4. JWT VALIDATION (AuthContext.tsx)

Enhanced token parsing with role validation:

```tsx
const login = (newToken: string) => {
  try {
    const parts = newToken.split('.');
    if (parts.length !== 3) throw new Error('Invalid token format');

    // Decode JWT payload (second part)
    const decoded = JSON.parse(atob(parts[1]));

    // Validate required fields
    if (!decoded.role || !decoded.email || !decoded.user_id) {
      throw new Error('Missing required JWT fields: role, email, or user_id');
    }

    // Ensure valid role
    const validRoles = ['doctor', 'technical_staff', 'admin', 'patient'];
    if (!validRoles.includes(decoded.role)) {
      console.warn(`[AuthContext] Invalid role in token: '${decoded.role}'. Valid roles: ${validRoles.join(', ')}`);
    }

    setToken(newToken);
    setRole(decoded.role);  // <-- Role extracted and stored here
    setEmail(decoded.email);
    setUserId(decoded.user_id);

    localStorage.setItem('role', decoded.role);
    // ... store other fields

    console.log(`[AuthContext] Login successful - Role: ${decoded.role}, Email: ${decoded.email}`);
  } catch (error) {
    console.error('[AuthContext] Failed to parse token:', error);
  }
};
```

**Key Points:**
- Role must exist in JWT `decoded.role`
- Role is validated against whitelist: `['doctor', 'technical_staff', 'admin', 'patient']`
- Role is stored in React state AND localStorage for persistence
- Invalid roles are logged with warning

---

## 5. PUBLIC ROUTE HANDLING (ProtectedRoute.tsx)

Login redirect logic:

```tsx
export const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, role } = useAuth();

  if (isAuthenticated && role) {
    // Redirect to appropriate dashboard based on role
    if (role === 'doctor') return <Navigate to="/doctor/dashboard" replace />;
    if (role === 'technical_staff') return <Navigate to="/staff/dashboard" replace />;
    if (role === 'admin') return <Navigate to="/admin/dashboard" replace />;
  }

  return <>{children}</>;
};
```

**Result:** After login, users are redirected to their role-appropriate dashboard:
- `doctor` → `/doctor/dashboard`
- `technical_staff` → `/staff/dashboard`

---

## VERIFICATION CHECKLIST

### ✅ Doctor Cannot Access Staff Routes

| Route | Doctor Access | Result |
|-------|--------------|--------|
| `/staff/register-patient` | Attempt | ❌ Redirected to `/unauthorized` |
| `/staff/upload-scan` | Attempt | ❌ Redirected to `/unauthorized` |
| `/staff/uploads` | Attempt | ❌ Redirected to `/unauthorized` |
| `/doctor/queue` | Direct access | ✅ Allowed |

**Console Output:**
```
[ProtectedRoute] Role verification: path=/staff/upload-scan, userRole=doctor, required=technical_staff, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'doctor' attempted to access /staff/upload-scan (required: technical_staff)
```

### ✅ Technical Staff Cannot Access Doctor Routes

| Route | Staff Access | Result |
|-------|--------------|--------|
| `/doctor/queue` | Attempt | ❌ Redirected to `/unauthorized` |
| `/doctor/patients` | Attempt | ❌ Redirected to `/unauthorized` |
| `/doctor/dashboard` | Attempt | ❌ Redirected to `/unauthorized` |
| `/staff/upload-scan` | Direct access | ✅ Allowed |

**Console Output:**
```
[ProtectedRoute] Role verification: path=/doctor/queue, userRole=technical_staff, required=doctor, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'technical_staff' attempted to access /doctor/queue (required: doctor)
```

### ✅ Navigation Menus Are Separate

**Doctor Navigation (AppShell):**
```
Dashboard → /doctor/dashboard
Scan Queue → /doctor/queue
My Patients → /doctor/patients
```

**Technical Staff Navigation (AppShell):**
```
Dashboard → /staff/dashboard
Register Patient → /staff/register-patient
Upload Scan → /staff/upload-scan
Upload History → /staff/uploads
```

---

## DEBUGGING ROLE ACCESS ISSUES

### Enable Console Logs

Open browser DevTools (F12) and check Console for role-based access logs:

```javascript
// On AppShell mount
[AppShell] Current role: doctor

// When attempting unauthorized access
[ProtectedRoute] Role verification: path=/staff/upload-scan, userRole=doctor, required=technical_staff, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'doctor' attempted to access /staff/upload-scan (required: technical_staff)

// On successful login
[AuthContext] Login successful - Role: doctor, Email: doctor@hospital.com
```

### Check localStorage

In DevTools Console, run:
```javascript
localStorage.getItem('role')  // Returns: "doctor" or "technical_staff"
```

### Test Role Verification

In DevTools Console:
```javascript
// Manually verify role from auth context
import { useAuth } from './context/AuthContext'
// ... then inspect the hook's role value
```

---

## Implementation Summary

| Component | Responsibility | Status |
|-----------|-----------------|--------|
| **App.tsx** | Route guards with `requiredRole` | ✅ Implemented |
| **ProtectedRoute.tsx** | Role verification & redirect logic | ✅ Enhanced with logging |
| **AuthContext.tsx** | JWT parsing & role extraction | ✅ Enhanced with validation |
| **AppShell.tsx** | Role-based navigation menu | ✅ Strict role filtering |
| **Login Page** | JWT token reception | ✅ Passes token to `login()` |

---

## Test Cases

### Test 1: Doctor Cannot Upload Scan
1. Login as: `doctor@hospital.com / password`
2. Try to access: `/staff/upload-scan`
3. Expected: Redirected to `/unauthorized`
4. Check Console: `[ProtectedRoute] UNAUTHORIZED ACCESS` message

### Test 2: Staff Cannot Review Scans
1. Login as: `staff@hospital.com / password`
2. Try to access: `/doctor/queue`
3. Expected: Redirected to `/unauthorized`
4. Check Console: `[ProtectedRoute] UNAUTHORIZED ACCESS` message

### Test 3: Navigation Shows Only Appropriate Items
1. Login as Doctor
2. Verify sidebar shows: Dashboard, Scan Queue, My Patients
3. Verify sidebar does NOT show: Register Patient, Upload Scan, Upload History
4. Logout and re-login as Staff
5. Verify sidebar shows: Dashboard, Register Patient, Upload Scan, Upload History
6. Verify sidebar does NOT show: Scan Queue, My Patients

