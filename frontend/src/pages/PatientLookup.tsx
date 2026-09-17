import React, { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatContext } from '../App';
import { EducationalChatWidget } from '../components/EducationalChatWidget';
import api from '../services/api';
import './PatientLookup.css';

export const PatientLookup: React.FC = () => {
  const [patientCode, setPatientCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [patientData, setPatientData] = useState<any>(null);
  const [showChat, setShowChat] = useState(false);
  const navigate = useNavigate();
  const { setIsChatOpen } = useContext(ChatContext);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await api.patientLookup(patientCode);
      setPatientData(data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Patient not found.');
      } else {
        setError(err.response?.data?.detail || 'Failed to retrieve patient data.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (patientData) {
    return (
      <div className="lookup-page">
        <nav className="lookup-navbar">
          <div className="lookup-navbar-content">
            <span className="logo">👁️ RetinalCare</span>
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/')}>
              Home
            </button>
          </div>
        </nav>

        <div className="lookup-container">
          <div className="lookup-card">
            <div className="lookup-header">
              <button
                className="btn btn-ghost"
                onClick={() => {
                  setPatientData(null);
                  setPatientCode('');
                }}
              >
                ← Back
              </button>
              <h1>Your Screening Results</h1>
            </div>

            <div className="patient-info">
              <div className="info-row">
                <span className="label">Patient Code:</span>
                <span className="value">{patientData.patient_code}</span>
              </div>
              <div className="info-row">
                <span className="label">Name:</span>
                <span className="value">{patientData.full_name}</span>
              </div>
              <div className="info-row">
                <span className="label">Date of Birth:</span>
                <span className="value">{patientData.date_of_birth}</span>
              </div>
              <div className="info-row">
                <span className="label">Sex:</span>
                <span className="value">{patientData.sex}</span>
              </div>
              <div className="info-row">
                <span className="label">Total Scans:</span>
                <span className="value">{patientData.total_scans}</span>
              </div>
            </div>

            {patientData.scans && patientData.scans.length > 0 ? (
              <div className="scans-list">
                <h2>Screening History</h2>
                {patientData.scans.map((scan: any, idx: number) => (
                  <div key={idx} className="scan-item card">
                    <div className="scan-date">
                      {new Date(scan.date).toLocaleDateString()}
                    </div>
                    <div className="scan-details">
                      <div className="detail-row">
                        <span className="label">AI Assessment:</span>
                        <span className={`grade grade-${scan.ai_grade}`}>
                          Grade {scan.ai_grade}: {scan.ai_severity}
                        </span>
                      </div>
                      {scan.doctor_grade !== null && (
                        <>
                          <div className="detail-row">
                            <span className="label">Doctor Assessment:</span>
                            <span className={`grade grade-${scan.doctor_grade}`}>
                              Grade {scan.doctor_grade}
                            </span>
                          </div>
                          <div className="detail-row">
                            <span className="label">Clinical Notes:</span>
                            <span className="notes">{scan.doctor_notes}</span>
                          </div>
                        </>
                      )}
                      <div className="detail-row">
                        <span className="label">Status:</span>
                        <span className={`status status-${scan.status}`}>
                          {scan.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="alert alert-info">No scans found for this patient.</div>
            )}

            {/* Educational Chat Widget - Inline on Patient Results */}
            <div style={{ marginTop: 'var(--spacing-8)' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: 'var(--spacing-4)',
              }}>
                <h2>📚 Learn About Your Condition</h2>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => setShowChat(!showChat)}
                >
                  {showChat ? '▼ Close' : '▶ Open Assistant'}
                </button>
              </div>
              {showChat && (
                <div style={{
                  border: '1px solid var(--color-gray-200)',
                  borderRadius: 'var(--radius-lg)',
                  overflow: 'hidden',
                  maxHeight: '500px',
                }}>
                  <EducationalChatWidget />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="lookup-page">
      <nav className="lookup-navbar">
        <div className="lookup-navbar-content">
          <span className="logo">👁️ RetinalCare</span>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/')}>
            Home
          </button>
        </div>
      </nav>

      <div className="lookup-container">
        <div className="lookup-card">
          <div className="lookup-header">
            <h1>Access Patient Space</h1>
            <p className="lookup-subtitle">
              When you were screened, your healthcare provider gave you a unique Patient ID.
              Enter it below along with your date of birth to securely view your results.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="lookup-form">
            <div className="form-group">
              <label htmlFor="patientCode">Patient ID</label>
              <input
                id="patientCode"
                type="text"
                placeholder="e.g., PAT-20260916-0001"
                value={patientCode}
                onChange={(e) => setPatientCode(e.target.value.toUpperCase())}
                required
                disabled={loading}
              />
              <small>Format: PAT-YYYYMMDD-NNNN (provided at screening)</small>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <button type="submit" className="btn btn-gold btn-lg" disabled={loading} style={{ width: '100%' }}>
              {loading ? 'Retrieving...' : 'View My Results'}
            </button>
          </form>

          <div className="lookup-divider">
            <span>or</span>
          </div>

          <div className="lookup-provider-section">
            <h3>Healthcare Provider Access</h3>
            <p>
              If you are a healthcare provider or technical staff member, log in to access
              patient management, scan review, and screening analytics tools.
            </p>
            <button
              className="btn btn-secondary btn-lg"
              onClick={() => navigate('/login')}
              style={{ width: '100%' }}
            >
              Provider Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
