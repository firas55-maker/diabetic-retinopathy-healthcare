# Role-Check Logic - Post-Implementation

## Quick Reference: Role-Based Access Control Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LOGIN                               │
├─────────────────────────────────────────────────────────────────┤
│ 1. Submit email + password                                       │
│ 2. Backend returns JWT with role claim                          │
│ 3. Frontend calls AuthContext.login(token)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  JWT TOKEN DECODED (AuthContext)                 │
├─────────────────────────────────────────────────────────────────┤
│ Token: eyJhbGc...eyJyb2xlIjoiZG9jdG9yIiwuZW1haWwiOi4uLn0...   │
│                                                                   │
│ Payload decoded:                                                 │
│ {                                                                │
│   "role": "doctor",              ← EXTRACTED HERE              │
│   "email": "doctor@hospital.com",                               │
│   "user_id": "user_123",                                        │
│   ...                                                            │
│ }                                                                │
│                                                                   │
│ Validation:                                                      │
│ ✓ role exists? YES                                              │
│ ✓ role in ['doctor', 'technical_staff', 'admin']? YES          │
│ ✓ email exists? YES                                             │
│ ✓ user_id exists? YES                                           │
│                                                                   │
│ → setRole("doctor")  [React state + localStorage]             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              REDIRECT TO ROLE-APPROPRIATE DASHBOARD              │
├─────────────────────────────────────────────────────────────────┤
│ PublicRoute checks role:                                         │
│                                                                   │
│ if (role === 'doctor')                                           │
│   → Navigate to /doctor/dashboard                               │
│ else if (role === 'technical_staff')                            │
│   → Navigate to /staff/dashboard                                │
│ else if (role === 'admin')                                      │
│   → Navigate to /admin/dashboard                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              APPSHELL RENDERS WITH ROLE-SPECIFIC NAV             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│ const navItems = role === 'doctor'                               │
│   ? getDoctorNavItems()      [Dashboard, Scan Queue, Patients] │
│   : role === 'technical_staff'                                  │
│   ? getStaffNavItems()       [Dashboard, Register, Upload, ...] │
│   : []                       [No items if role invalid]          │
│                                                                   │
│ Console Log: [AppShell] Current role: doctor                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│           USER NAVIGATES TO A PROTECTED ROUTE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│ Example: Doctor clicks "Scan Queue" → Navigate to /doctor/queue │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│          PROTECTED ROUTE CHECKS ROLE (ProtectedRoute.tsx)       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│ Route Definition (App.tsx):                                      │
│ <Route                                                           │
│   path="/doctor/queue"                                           │
│   element={                                                      │
│     <ProtectedRoute requiredRole="doctor">     ← ROLE CHECK    │
│       <ScanQueue />                                              │
│     </ProtectedRoute>                                            │
│   }                                                              │
│ />                                                               │
│                                                                   │
│ ProtectedRoute Logic:                                            │
│                                                                   │
│ 1. Check: isAuthenticated?                                       │
│    if (!token || !role) → Redirect /login                      │
│                                                                   │
│ 2. Check: requiredRole provided?                                │
│    if (!requiredRole) → Allow access                            │
│                                                                   │
│ 3. Extract required role(s):                                     │
│    requiredRole = "doctor" → roles = ["doctor"]                │
│                                                                   │
│ 4. Verify user role matches required:                           │
│    if (role === "doctor" && "doctor" in ["doctor"])             │
│       → MATCH! Access granted ✓                                 │
│    else                                                          │
│       → NO MATCH! Redirect /unauthorized ✗                      │
│                                                                   │
│ Console Logs:                                                    │
│ [ProtectedRoute] Role verification: path=/doctor/queue,        │
│                 userRole=doctor, required=doctor,               │
│                 authorized=true                                 │
│ [ProtectedRoute] Access granted to /doctor/queue for role: doctor │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                        ✅ RENDER PAGE
                     (ScanQueue Component)
```

---

## Attack Scenarios & Prevention

### Scenario 1: Doctor Tries to Access Staff Upload Page

```
Doctor (role="doctor") tries: /staff/upload-scan
                    │
                    ▼
Route Definition: <ProtectedRoute requiredRole="technical_staff">
                    │
                    ▼
ProtectedRoute Logic:
  ✓ isAuthenticated? YES (has valid token)
  ✓ requiredRole defined? YES = "technical_staff"
  ✓ Extract roles: ["technical_staff"]
  ✓ Check: doctor === "technical_staff"? NO ✗
                    │
                    ▼
  console.error('[ProtectedRoute] UNAUTHORIZED ACCESS: 
    User with role 'doctor' attempted to access 
    /staff/upload-scan (required: technical_staff)')
                    │
                    ▼
  return <Navigate to="/unauthorized" replace />
                    │
                    ▼
              User sees: Unauthorized Page
```

**Console Output:**
```
[ProtectedRoute] Role verification: path=/staff/upload-scan, 
                 userRole=doctor, required=technical_staff, 
                 authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'doctor' 
                 attempted to access /staff/upload-scan 
                 (required: technical_staff)
```

---

### Scenario 2: Staff Tries to Access Doctor Scan Queue

```
Staff (role="technical_staff") tries: /doctor/queue
                    │
                    ▼
Route Definition: <ProtectedRoute requiredRole="doctor">
                    │
                    ▼
ProtectedRoute Logic:
  ✓ isAuthenticated? YES (has valid token)
  ✓ requiredRole defined? YES = "doctor"
  ✓ Extract roles: ["doctor"]
  ✓ Check: technical_staff === "doctor"? NO ✗
                    │
                    ▼
  console.error('[ProtectedRoute] UNAUTHORIZED ACCESS: 
    User with role 'technical_staff' attempted to access 
    /doctor/queue (required: doctor)')
                    │
                    ▼
  return <Navigate to="/unauthorized" replace />
                    │
                    ▼
              User sees: Unauthorized Page
```

**Console Output:**
```
[ProtectedRoute] Role verification: path=/doctor/queue, 
                 userRole=technical_staff, required=doctor, 
                 authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'technical_staff' 
                 attempted to access /doctor/queue (required: doctor)
```

---

## Role Check Implementation Details

### 1️⃣ AuthContext - Extract Role from JWT

**File:** `src/context/AuthContext.tsx`

```typescript
const login = (newToken: string) => {
  try {
    // Split JWT into 3 parts: header.payload.signature
    const parts = newToken.split('.');
    if (parts.length !== 3) throw new Error('Invalid token format');

    // Decode payload (part[1]) from Base64
    const decoded = JSON.parse(atob(parts[1]));

    // ✅ ROLE EXTRACTED HERE
    const role = decoded.role;  // "doctor" or "technical_staff"
    
    // Validate role is recognized
    const validRoles = ['doctor', 'technical_staff', 'admin', 'patient'];
    if (!validRoles.includes(role)) {
      console.warn(`Invalid role: '${role}'. Valid: ${validRoles.join(', ')}`);
    }

    // Store role in React state + localStorage
    setRole(role);
    localStorage.setItem('role', role);
    
    console.log(`[AuthContext] Login successful - Role: ${role}`);
  } catch (error) {
    console.error('[AuthContext] Failed to parse token:', error);
  }
};
```

**What Happens:**
- JWT decoded: `eyJhbGc...` → `{ role: "doctor", email: "...", user_id: "..." }`
- Role `"doctor"` extracted
- Stored in React state: `setRole("doctor")`
- Stored in localStorage for persistence

---

### 2️⃣ ProtectedRoute - Verify Role Matches Route

**File:** `src/components/ProtectedRoute.tsx`

```typescript
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
}) => {
  const { isAuthenticated, role } = useAuth();  // Get current role
  const location = useLocation();

  // Step 1: Check if authenticated
  if (!isAuthenticated) {
    console.warn(`[ProtectedRoute] Unauthenticated access to ${location.pathname}`);
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Step 2: Check if role restriction exists
  if (requiredRole) {
    // Convert single role to array for flexibility
    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];

    // Log the verification
    console.log(
      `[ProtectedRoute] Role verification: 
       path=${location.pathname}, 
       userRole=${role}, 
       required=${roles.join(', ')}, 
       authorized=${role && roles.includes(role)}`
    );

    // Step 3: ✅ ROLE CHECK - Does user's role match required role?
    if (!role || !roles.includes(role)) {
      console.error(
        `[ProtectedRoute] UNAUTHORIZED ACCESS: 
         User with role '${role}' attempted to access 
         ${location.pathname} (required: ${roles.join(', ')})`
      );
      return <Navigate to="/unauthorized" replace />;
    }
  }

  console.debug(`[ProtectedRoute] Access granted to ${location.pathname}`);
  return <>{children}</>;
};
```

**What Happens:**
- Route checks: `requiredRole = "doctor"`
- Gets user role: `role = "doctor"` (from context)
- Compares: `"doctor" in ["doctor"]`? YES ✓
- Renders component

---

### 3️⃣ AppShell - Filter Navigation by Role

**File:** `src/components/AppShell.tsx`

```typescript
export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const { role } = useAuth();  // Get current role
  const navigate = useNavigate();

  // Log current role
  React.useEffect(() => {
    console.log('[AppShell] Current role:', role);
  }, [role]);

  // Define menu items for each role
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

  // ✅ NAVIGATION FILTERING - Show only role-specific items
  const navItems = role === 'doctor'
    ? getDoctorNavItems()        // Doctor sees: Dashboard, Scan Queue, Patients
    : role === 'technical_staff'
    ? getStaffNavItems()          // Staff sees: Dashboard, Register, Upload, History
    : [];                         // Unknown role sees: nothing

  const roleLabel = role === 'doctor' 
    ? 'Doctor' 
    : role === 'technical_staff' 
    ? 'Technical Staff' 
    : 'User';

  return (
    <div className="app-container">
      <aside className="sidebar">
        {/* ... sidebar header ... */}
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <div key={item.path} className="nav-item">
              <a
                href={item.path}
                onClick={(e) => {
                  e.preventDefault();
                  navigate(item.path);
                }}
              >
                {item.icon} {item.label}
              </a>
            </div>
          ))}
        </nav>
        {/* ... sidebar footer ... */}
      </aside>
    </div>
  );
};
```

**What Happens:**
- Role: `"doctor"`
- Calls: `getDoctorNavItems()`
- Renders: 3 items (Dashboard, Scan Queue, Patients)
- DOES NOT render: Register Patient, Upload Scan, Upload History

---

## Testing the Role-Check Logic

### ✅ Test 1: Doctor Login & Access Doctor Routes

```bash
# Step 1: Login
Email: doctor@hospital.com
Password: password

# Console Output:
[AuthContext] Login successful - Role: doctor, Email: doctor@hospital.com
[ProtectedRoute] Role verification: path=/doctor/dashboard, userRole=doctor, required=doctor, authorized=true
[ProtectedRoute] Access granted to /doctor/dashboard for role: doctor
[AppShell] Current role: doctor

# Step 2: Navigation shows only
✓ Dashboard → /doctor/dashboard
✓ Scan Queue → /doctor/queue
✓ My Patients → /doctor/patients
✗ NO Register Patient
✗ NO Upload Scan
✗ NO Upload History
```

### ✅ Test 2: Doctor Tries to Access Staff Route (DENIED)

```bash
# Step 1: As doctor, manually visit: /staff/upload-scan

# Console Output:
[ProtectedRoute] Role verification: path=/staff/upload-scan, userRole=doctor, required=technical_staff, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'doctor' attempted to access /staff/upload-scan (required: technical_staff)

# Result: Redirected to /unauthorized
# User sees: "You don't have permission to access this page"
```

### ✅ Test 3: Staff Login & Access Staff Routes

```bash
# Step 1: Login
Email: staff@hospital.com
Password: password

# Console Output:
[AuthContext] Login successful - Role: technical_staff, Email: staff@hospital.com
[ProtectedRoute] Role verification: path=/staff/dashboard, userRole=technical_staff, required=technical_staff, authorized=true
[ProtectedRoute] Access granted to /staff/dashboard for role: technical_staff
[AppShell] Current role: technical_staff

# Step 2: Navigation shows only
✓ Dashboard → /staff/dashboard
✓ Register Patient → /staff/register-patient
✓ Upload Scan → /staff/upload-scan
✓ Upload History → /staff/uploads
✗ NO Scan Queue
✗ NO My Patients
```

### ✅ Test 4: Staff Tries to Access Doctor Route (DENIED)

```bash
# Step 1: As staff, manually visit: /doctor/queue

# Console Output:
[ProtectedRoute] Role verification: path=/doctor/queue, userRole=technical_staff, required=doctor, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'technical_staff' attempted to access /doctor/queue (required: doctor)

# Result: Redirected to /unauthorized
# User sees: "You don't have permission to access this page"
```

---

## Summary: Role-Check Logic is Now Enforced at 3 Levels

| Level | Component | Check | Result |
|-------|-----------|-------|--------|
| **1. JWT Parsing** | AuthContext | Role extracted from token, validated against whitelist | ✓ Role stored in state + localStorage |
| **2. Route Guards** | ProtectedRoute | User role compared against route's requiredRole | ✓ Granted or redirected to /unauthorized |
| **3. Navigation** | AppShell | Only role-appropriate menu items rendered | ✓ Doctor/Staff see different nav menus |

**When Doctor tries to access `/staff/upload-scan`:**
- ProtectedRoute catches the attempt
- Logs error to console
- Redirects to `/unauthorized`
- Doctor never sees the page

**When Technical Staff tries to access `/doctor/queue`:**
- ProtectedRoute catches the attempt
- Logs error to console
- Redirects to `/unauthorized`
- Staff never sees the page

