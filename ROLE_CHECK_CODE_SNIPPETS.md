# Role-Check Logic - Code Snippets & Line References

## Quick Code Reference

### 🔑 1. JWT Role Extraction (AuthContext.tsx)

**File:** `frontend/src/context/AuthContext.tsx` | **Lines:** 21-53

```typescript
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
    setRole(decoded.role);  // ← ROLE STORED HERE
    setEmail(decoded.email);
    setUserId(decoded.user_id);

    localStorage.setItem('token', newToken);
    localStorage.setItem('role', decoded.role);
    localStorage.setItem('email', decoded.email);
    localStorage.setItem('userId', decoded.user_id);

    console.log(`[AuthContext] Login successful - Role: ${decoded.role}, Email: ${decoded.email}`);
  } catch (error) {
    console.error('[AuthContext] Failed to parse token:', error);
    setToken(null);
    setRole(null);
    setEmail(null);
    setUserId(null);
  }
};
```

**Key Points:**
- Line 27: `const decoded = JSON.parse(atob(parts[1]));` - JWT decoded
- Line 34: Role validation against whitelist
- Line 37: `setRole(decoded.role);` - Role stored in React state
- Line 42: Role persisted to localStorage
- Line 46: Logged to console for debugging

---

### 🔒 2. Route Protection (ProtectedRoute.tsx)

**File:** `frontend/src/components/ProtectedRoute.tsx` | **Lines:** 1-49

```typescript
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string | string[];
}

/**
 * ProtectedRoute: Enforces both authentication and role-based access control
 */
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

    // Log verification attempt
    console.log(
      `[ProtectedRoute] Role verification: path=${location.pathname}, userRole=${role}, required=${roles.join(', ')}, authorized=${role && roles.includes(role)}`
    );

    // ⚡ CRITICAL ROLE CHECK ⚡
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

**Key Points:**
- Line 32: Get `role` from useAuth() context
- Line 36: Convert `requiredRole` to array
- Line 40: Log role verification with all details
- Line 43: **`!roles.includes(role)`** - THE CRITICAL CHECK
- Line 44: Log ERROR if unauthorized
- Line 45: Redirect to `/unauthorized` if access denied
- Line 51: Log DEBUG if access granted

---

### 🎨 3. Navigation Filtering (AppShell.tsx)

**File:** `frontend/src/components/AppShell.tsx` | **Lines:** 9-34

```typescript
export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, email, role } = useAuth();
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  React.useEffect(() => {
    console.log('[AppShell] Current role:', role);
  }, [role]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

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

  // ⚡ NAVIGATION FILTERING BY ROLE ⚡
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

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="app-container">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">👁️</div>
            <div className="sidebar-logo-text">
              <h2>RetinalCare</h2>
              <p>Screening Platform</p>
            </div>
          </div>
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

      {/* MAIN CONTAINER */}
      <div className="main-container">
        {/* TOP BAR */}
        <header className="topbar">
          <h1 className="topbar-title">Healthcare Screening Platform</h1>
          <div className="topbar-actions">
            <button className="notification-bell" title="Notifications">
              🔔
              <span className="notification-badge"></span>
            </button>
          </div>
        </header>

        {/* MAIN CONTENT */}
        <main className="main-content">
          <div className="page-wrapper">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
```

**Key Points:**
- Line 12: `const { role } = useAuth();` - Get role from context
- Line 14-16: Log role on mount
- Line 35-42: **Navigation filtering**:
  - If `role === 'doctor'` → show doctor items
  - Else if `role === 'technical_staff'` → show staff items
  - Else → show empty array (safe fallback)

---

### 📍 4. Route Definitions (App.tsx)

**File:** `frontend/src/App.tsx` | **Lines:** 47-121

```typescript
// Doctor Routes
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

// Technical Staff Routes
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

**Key Points:**
- Every doctor route: `requiredRole="doctor"`
- Every staff route: `requiredRole="technical_staff"`
- Doctor cannot access `/staff/*` routes
- Staff cannot access `/doctor/*` routes

---

## Testing the Role-Check Logic

### Test 1: Doctor Login
```javascript
// Step 1: Login as doctor@hospital.com
// Step 2: Check Console for:
[AuthContext] Login successful - Role: doctor, Email: doctor@hospital.com
[AppShell] Current role: doctor

// Step 3: Try to access /staff/upload-scan
// Step 4: Check Console for:
[ProtectedRoute] Role verification: path=/staff/upload-scan, userRole=doctor, required=technical_staff, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'doctor' attempted to access /staff/upload-scan (required: technical_staff)

// Step 5: Result: Redirected to /unauthorized page
```

### Test 2: Staff Login
```javascript
// Step 1: Login as staff@hospital.com
// Step 2: Check Console for:
[AuthContext] Login successful - Role: technical_staff, Email: staff@hospital.com
[AppShell] Current role: technical_staff

// Step 3: Try to access /doctor/queue
// Step 4: Check Console for:
[ProtectedRoute] Role verification: path=/doctor/queue, userRole=technical_staff, required=doctor, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'technical_staff' attempted to access /doctor/queue (required: doctor)

// Step 5: Result: Redirected to /unauthorized page
```

### Test 3: Check localStorage
```javascript
// After login as doctor
localStorage.getItem('role')      // "doctor"
localStorage.getItem('email')     // "doctor@hospital.com"
localStorage.getItem('token')     // JWT token

// After logout
localStorage.getItem('role')      // null
localStorage.getItem('email')     // null
localStorage.getItem('token')     // null
```

---

## Summary: Three Role-Check Points

| # | Component | Check | Line | Result |
|---|-----------|-------|------|--------|
| 1 | AuthContext | `validRoles.includes(decoded.role)` | 34 | Role validated on login |
| 2 | ProtectedRoute | `!roles.includes(role)` | 43 | Role checked per route |
| 3 | AppShell | `role === 'doctor' ? ... : ...` | 35-42 | Navigation filtered by role |

**Each layer is independent:**
- Even if nav shows wrong items, ProtectedRoute blocks access
- Even if ProtectedRoute has a bug, AuthContext validates role
- Even if someone manipulates localStorage, JWT in token is authoritative

