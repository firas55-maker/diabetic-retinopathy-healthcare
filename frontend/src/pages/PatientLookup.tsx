import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './PatientLookup.css';

export const PatientLookup: React.FC = () => {
  const [patientCode, setPatientCode] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [patientData, setPatientData] = useState<any>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await api.patientLookup(patientCode, dateOfBirth);
      setPatientData(data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Date of birth does not match. Access denied.');
      } else if (err.response?.status === 404) {
        setError('Patient not found.');
      } else {
        setError(err.response?.data?.detail || 'Failed to retrieve patient data.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLoginRedirect = () => {
    navigate('/login');
  };

  if (patientData) {
    return (
      <div className="lookup-container">
        <div className="lookup-card">
          <div className="lookup-header">
            <h1>Your Scan History</h1>
            <button
              className="btn btn-secondary"
              onClick={() => {
                setPatientData(null);
                setPatientCode('');
                setDateOfBirth('');
              }}
            >
              ← Back to Search
            </button>
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
              <h2>Scans</h2>
              {patientData.scans.map((scan: any, idx: number) => (
                <div key={idx} className="scan-item">
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
        </div>
      </div>
    );
  }

  return (
    <div className="lookup-container">
      <div className="lookup-card">
        <div className="lookup-header">
          <h1>Healthcare Screening System</h1>
          <p>Patient Scan Lookup</p>
        </div>

        <form onSubmit={handleSubmit} className="lookup-form">
          <p className="form-description">
            Enter your patient code and date of birth to view your scan history and assessments.
          </p>

          <div className="form-group">
            <label htmlFor="patientCode">Patient Code</label>
            <input
              id="patientCode"
              type="text"
              placeholder="e.g., PAT-20260916-0001"
              value={patientCode}
              onChange={(e) => setPatientCode(e.target.value.toUpperCase())}
              required
              disabled={loading}
            />
            <small>Format: PAT-YYYYMMDD-NNNN</small>
          </div>

          <div className="form-group">
            <label htmlFor="dob">Date of Birth</label>
            <input
              id="dob"
              type="date"
              value={dateOfBirth}
              onChange={(e) => setDateOfBirth(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
            {loading ? 'Searching...' : 'View My Scans'}
          </button>
        </form>

        <div className="lookup-footer">
          <div className="footer-section">
            <h3>Healthcare Provider?</h3>
            <p>Staff members and doctors can log in to access additional features.</p>
            <button className="btn btn-secondary" onClick={handleLoginRedirect}>
              Staff Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
