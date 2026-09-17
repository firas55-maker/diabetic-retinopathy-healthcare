# Role-Check Logic - Quick Reference Guide

## 🎯 The 3-Point Role Enforcement System

### Point 1️⃣: JWT Role Extraction (Login)
**File:** `frontend/src/context/AuthContext.tsx`

```typescript
// When user logs in, JWT token is decoded
const login = (newToken: string) => {
  const decoded = JSON.parse(atob(newToken.split('.')[1]));
  
  // 🔑 ROLE EXTRACTED HERE
  const role = decoded.role;  // "doctor" or "technical_staff"
  
  setRole(role);                    // Store in React state
  localStorage.setItem('role', role); // Persist for page refresh
  
  console.log(`[AuthContext] Login successful - Role: ${role}`);
};
```

**What Happens:**
- Token: `eyJhbGc...payload_with_role...signature`
- Payload decoded: `{ role: "doctor", email: "doctor@hospital.com", user_id: "123" }`
- Role stored: `React state + localStorage`
- Logged: `[AuthContext] Login successful - Role: doctor`

---

### Point 2️⃣: Route Protection (Route Access)
**File:** `frontend/src/App.tsx` + `frontend/src/components/ProtectedRoute.tsx`

```typescript
// Route definition
<Route
  path="/doctor/queue"
  element={
    <ProtectedRoute requiredRole="doctor">  // ← Only doctors allowed
      <ScanQueue />
    </ProtectedRoute>
  }
/>

// ProtectedRoute component
export const ProtectedRoute = ({ children, requiredRole }) => {
  const { role } = useAuth();
  
  if (requiredRole) {
    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    
    // 🔒 CRITICAL CHECK: Does user's role match required role?
    if (!role || !roles.includes(role)) {
      console.error(`UNAUTHORIZED: role '${role}' cannot access route requiring '${requiredRole}'`);
      return <Navigate to="/unauthorized" replace />;  // ❌ DENY
    }
  }
  
  console.debug(`Access granted to ${requiredRole}`);
  return <>{children}</>;  // ✅ ALLOW
};
```

**What Happens:**
- Doctor tries to access `/doctor/queue`
  - ProtectedRoute checks: `requiredRole = "doctor"`
  - Compares: user `role = "doctor"` vs required `"doctor"`
  - Result: `"doctor" === "doctor"` ✅ → Access granted
  
- Doctor tries to access `/staff/upload-scan`
  - ProtectedRoute checks: `requiredRole = "technical_staff"`
  - Compares: user `role = "doctor"` vs required `"technical_staff"`
  - Result: `"doctor" !== "technical_staff"` ❌ → Redirected to `/unauthorized`

---

### Point 3️⃣: Navigation Filtering (UI)
**File:** `frontend/src/components/AppShell.tsx`

```typescript
export const AppShell = ({ children }) => {
  const { role } = useAuth();
  
  // 🎨 NAVIGATION FILTERING
  const navItems = role === 'doctor'
    ? [
        { label: 'Dashboard', path: '/doctor/dashboard' },
        { label: 'Scan Queue', path: '/doctor/queue' },
        { label: 'My Patients', path: '/doctor/patients' },
      ]
    : role === 'technical_staff'
    ? [
        { label: 'Dashboard', path: '/staff/dashboard' },
        { label: 'Register Patient', path: '/staff/register-patient' },
        { label: 'Upload Scan', path: '/staff/upload-scan' },
        { label: 'Upload History', path: '/staff/uploads' },
      ]
    : [];  // Empty if role is unknown
  
  return (
    <div className="app-container">
      <aside className="sidebar">
        <nav>
          {navItems.map((item) => (
            <a key={item.path} href={item.path}>{item.label}</a>
          ))}
        </nav>
      </aside>
    </div>
  );
};
```

**What Happens:**
- If `role = "doctor"`
  - Renders: Dashboard, Scan Queue, My Patients
  - Does NOT render: Register Patient, Upload Scan, Upload History
  
- If `role = "technical_staff"`
  - Renders: Dashboard, Register Patient, Upload Scan, Upload History
  - Does NOT render: Scan Queue, My Patients

---

## 📊 Role-Check Decision Tree

```
User Action: Try to access /doctor/queue
    │
    ├─ Doctor with valid token?
    │  └─ YES → Continue
    │
    ├─ Route requires role="doctor"?
    │  └─ YES → Continue
    │
    ├─ Check: user.role === "doctor"?
    │  ├─ YES → ✅ GRANT ACCESS
    │  │       (Render ScanQueue component)
    │  │       Log: [ProtectedRoute] Access granted
    │  │
    │  └─ NO (role is "technical_staff")
    │      └─ ❌ DENY ACCESS
    │         (Redirect to /unauthorized)
    │         Log: [ProtectedRoute] UNAUTHORIZED ACCESS
```

---

## 🧪 Real-World Test Cases

### Test 1: Doctor Login & Access Doctor Route ✅

```
1. Login as doctor@hospital.com
   Console: [AuthContext] Login successful - Role: doctor

2. Navigate to /doctor/queue
   Console: [ProtectedRoute] Role verification: userRole=doctor, required=doctor, authorized=true
   Console: [ProtectedRoute] Access granted to /doctor/queue
   Result: Scan Queue page loads

3. Sidebar shows:
   ✓ Dashboard
   ✓ Scan Queue
   ✓ My Patients
   ✗ Register Patient (not visible)
   ✗ Upload Scan (not visible)
```

### Test 2: Doctor Tries to Access Staff Route ❌

```
1. As doctor, manually navigate to /staff/upload-scan
   Console: [ProtectedRoute] Role verification: path=/staff/upload-scan, 
                             userRole=doctor, required=technical_staff, authorized=false
   Console: [ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'doctor' 
                             attempted to access /staff/upload-scan (required: technical_staff)
   Result: Redirected to /unauthorized page

2. Sidebar still shows only doctor items
   (Upload Scan not visible)
```

### Test 3: Staff Login & Access Staff Route ✅

```
1. Login as staff@hospital.com
   Console: [AuthContext] Login successful - Role: technical_staff

2. Navigate to /staff/upload-scan
   Console: [ProtectedRoute] Role verification: userRole=technical_staff, required=technical_staff, authorized=true
   Console: [ProtectedRoute] Access granted to /staff/upload-scan
   Result: UploadScan page loads

3. Sidebar shows:
   ✓ Dashboard
   ✓ Register Patient
   ✓ Upload Scan
   ✓ Upload History
   ✗ Scan Queue (not visible)
   ✗ My Patients (not visible)
```

### Test 4: Staff Tries to Access Doctor Route ❌

```
1. As staff, manually navigate to /doctor/queue
   Console: [ProtectedRoute] Role verification: path=/doctor/queue, 
                             userRole=technical_staff, required=doctor, authorized=false
   Console: [ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'technical_staff' 
                             attempted to access /doctor/queue (required: doctor)
   Result: Redirected to /unauthorized page

2. Sidebar still shows only staff items
   (Scan Queue not visible)
```

---

## 🔍 Console Logs for Debugging

### Successful Login (Doctor)
```
[AuthContext] Login successful - Role: doctor, Email: doctor@hospital.com
[AppShell] Current role: doctor
[ProtectedRoute] Access granted to /doctor/dashboard for role: doctor
```

### Unsuccessful Access Attempt (Doctor → Staff Route)
```
[ProtectedRoute] Role verification: path=/staff/upload-scan, 
                 userRole=doctor, required=technical_staff, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'doctor' attempted to access 
                 /staff/upload-scan (required: technical_staff)
```

### Successful Login (Staff)
```
[AuthContext] Login successful - Role: technical_staff, Email: staff@hospital.com
[AppShell] Current role: technical_staff
[ProtectedRoute] Access granted to /staff/upload-scan for role: technical_staff
```

### Unsuccessful Access Attempt (Staff → Doctor Route)
```
[ProtectedRoute] Role verification: path=/doctor/queue, 
                 userRole=technical_staff, required=doctor, authorized=false
[ProtectedRoute] UNAUTHORIZED ACCESS: User with role 'technical_staff' attempted to access 
                 /doctor/queue (required: doctor)
```

---

## 🛡️ Security Guarantees

| Scenario | Protection | Enforced By |
|----------|-----------|------------|
| Doctor accesses `/staff/upload-scan` via URL | ❌ Denied, redirected to /unauthorized | ProtectedRoute |
| Staff accesses `/doctor/queue` via URL | ❌ Denied, redirected to /unauthorized | ProtectedRoute |
| Doctor sees upload options in nav menu | ❌ Not shown | AppShell (role filter) |
| Staff sees scan queue in nav menu | ❌ Not shown | AppShell (role filter) |
| Unknown role accesses any route | ❌ Denied | ProtectedRoute + AppShell |
| Unauthenticated user accesses protected route | ❌ Redirected to /login | ProtectedRoute |

---

## 📋 Complete Role Mapping

### Doctor Routes (require `role="doctor"`)
```
✓ /doctor/dashboard          (Dashboard page)
✓ /doctor/queue              (Scan Queue)
✓ /doctor/patients           (My Patients list)
✓ /doctor/patients/:id       (Patient details)
✓ /doctor/scan/:id           (Scan review)
```

### Staff Routes (require `role="technical_staff"`)
```
✓ /staff/dashboard           (Dashboard)
✓ /staff/register-patient    (Register new patient)
✓ /staff/upload-scan         (Upload retinal scan)
✓ /staff/uploads             (Upload history)
```

### Doctor Navigation Items
```
Dashboard    → /doctor/dashboard
Scan Queue   → /doctor/queue
My Patients  → /doctor/patients
```

### Staff Navigation Items
```
Dashboard         → /staff/dashboard
Register Patient  → /staff/register-patient
Upload Scan       → /staff/upload-scan
Upload History    → /staff/uploads
```

---

## ✅ Verification: Role-Check is Working

**To verify role-checks are working:**

1. Open DevTools (F12)
2. Go to Console tab
3. Login as Doctor
   - Should see: `[AuthContext] Login successful - Role: doctor`
   - Sidebar should show: Dashboard, Scan Queue, My Patients
4. Type in URL bar: `http://localhost/staff/upload-scan`
5. Press Enter
   - Should see: `[ProtectedRoute] UNAUTHORIZED ACCESS`
   - Should redirect to `/unauthorized`
6. Logout, login as Staff
   - Should see: `[AuthContext] Login successful - Role: technical_staff`
   - Sidebar should show: Dashboard, Register Patient, Upload Scan, Upload History
7. Type in URL bar: `http://localhost/doctor/queue`
8. Press Enter
   - Should see: `[ProtectedRoute] UNAUTHORIZED ACCESS`
   - Should redirect to `/unauthorized`

**If all 8 steps work as described, role-based access control is properly enforced.**

