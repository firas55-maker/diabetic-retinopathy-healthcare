import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute, PublicRoute } from './components/ProtectedRoute';
import { EducationalChatWidget } from './components/EducationalChatWidget';

// Pages
import { Landing } from './pages/Landing';
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

// Global chat context
export const ChatContext = React.createContext<{
  isChatOpen: boolean;
  setIsChatOpen: (open: boolean) => void;
}>({
  isChatOpen: false,
  setIsChatOpen: () => {},
});

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <ChatContext.Provider value={{ isChatOpen, setIsChatOpen }}>
      <Router>
        <AuthProvider>
          {/* Global Chat Widget - Fixed Drawer */}
          {isChatOpen && (
            <div style={{
              position: 'fixed',
              bottom: 0,
              right: 0,
              width: '400px',
              height: '600px',
              zIndex: 9999,
              boxShadow: '0 -2px 10px rgba(0, 0, 0, 0.1)',
              borderRadius: '8px 8px 0 0',
            }}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                background: 'white',
                borderRadius: '8px 8px 0 0',
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px 16px',
                  borderBottom: '1px solid #e0e0e0',
                }}>
                  <span style={{ fontSize: '14px', fontWeight: 600 }}>Close</span>
                  <button
                    onClick={() => setIsChatOpen(false)}
                    style={{
                      background: 'none',
                      border: 'none',
                      fontSize: '20px',
                      cursor: 'pointer',
                      padding: '0',
                    }}
                  >
                    ✕
                  </button>
                </div>
                <div style={{ flex: 1, overflow: 'auto' }}>
                  <EducationalChatWidget />
                </div>
              </div>
            </div>
          )}

          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Landing />} />
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
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </Router>
    </ChatContext.Provider>
  );
}

export default App;
