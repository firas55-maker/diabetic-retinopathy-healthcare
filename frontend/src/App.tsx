import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute, PublicRoute } from './components/ProtectedRoute';

// Pages
import { Login } from './pages/Login';
import { DoctorDashboard } from './pages/doctor/Dashboard';
import { DoctorPatients } from './pages/doctor/Patients';
import { PatientDetails } from './pages/doctor/PatientDetails';
import { ScanQueue } from './pages/doctor/ScanQueue';
import { ScanReview } from './pages/doctor/ScanReview';

import { StaffDashboard } from './pages/staff/Dashboard';
import { RegisterPatient } from './pages/staff/RegisterPatient';
import { UploadScan } from './pages/staff/UploadScan';
import { UploadHistory } from './pages/staff/UploadHistory';

import { PatientPortal } from './pages/patient/Portal';
import { PatientLookup } from './pages/PatientLookup';
import { Unauthorized } from './pages/Unauthorized';

// Styles
import './styles/variables.css';
import './styles/global.css';
import './styles/components.css';
import './styles/layout.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
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
            path="/doctor/queue"
            element={
              <ProtectedRoute requiredRole="doctor">
                <ScanQueue />
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

          {/* Catch-all */}
          <Route path="/" element={<Navigate to="/patient-lookup" replace />} />
          <Route path="*" element={<Navigate to="/patient-lookup" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
