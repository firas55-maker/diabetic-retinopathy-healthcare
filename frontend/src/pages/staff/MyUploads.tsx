import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Sidebar } from '../../components/Sidebar';
import api from '../../services/api';

export const MyUploads: React.FC = () => {
  const { email, role } = useAuth();
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUploads();
  }, []);

  const fetchUploads = async () => {
    try {
      const data = await api.getMyScans(0, 100);
      setScans(data.scans || []);
    } catch (err: any) {
      setError('Failed to load uploads');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!email || !role) return <div>Loading...</div>;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending_review':
        return 'badge-pending';
      case 'reviewed':
        return 'badge-reviewed';
      default:
        return 'badge-info';
    }
  };

  const stats = {
    total: scans.length,
    pending: scans.filter((s) => s.status === 'pending_review').length,
    reviewed: scans.filter((s) => s.status === 'reviewed').length,
  };

  return (
    <div className="dashboard-container">
      <Sidebar role={role} email={email} />
      <div className="main-content">
        <div className="header">
          <h1>My Scan Uploads</h1>
          <div className="user-info">
            <strong>{email}</strong>
            <p>Total uploads: {stats.total}</p>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid-3">
          <div className="stat-card">
            <h3>Total Uploads</h3>
            <div className="stat-card-value">{stats.total}</div>
            <p className="stat-card-label">scans</p>
          </div>
          <div className="stat-card">
            <h3>Pending Review</h3>
            <div className="stat-card-value">{stats.pending}</div>
            <p className="stat-card-label">awaiting doctor</p>
          </div>
          <div className="stat-card">
            <h3>Reviewed</h3>
            <div className="stat-card-value">{stats.reviewed}</div>
            <p className="stat-card-label">completed</p>
          </div>
        </div>

        {loading ? (
          <div className="spinner"></div>
        ) : error ? (
          <div className="alert alert-error">{error}</div>
        ) : scans.length > 0 ? (
          <div className="card">
            <h2>Upload History</h2>
            <table className="table">
              <thead>
                <tr>
                  <th>Patient Code</th>
                  <th>AI Grade</th>
                  <th>Confidence</th>
                  <th>Status</th>
                  <th>Doctor Grade</th>
                  <th>Uploaded</th>
                  <th>Reviewed</th>
                </tr>
              </thead>
              <tbody>
                {scans.map((scan) => (
                  <tr key={scan.id}>
                    <td>{scan.patient_code}</td>
                    <td>
                      <span className={`badge badge-${['success', 'warning', 'danger', 'danger'][scan.ai_grade] || 'info'}`}>
                        {scan.ai_grade} - {scan.ai_severity}
                      </span>
                    </td>
                    <td>{(scan.ai_confidence * 100).toFixed(1)}%</td>
                    <td>
                      <span className={`badge ${getStatusColor(scan.status)}`}>
                        {scan.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td>
                      {scan.doctor_grade !== null ? (
                        <span className={`badge badge-${['success', 'warning', 'danger', 'danger'][scan.doctor_grade] || 'info'}`}>
                          {scan.doctor_grade}
                        </span>
                      ) : (
                        <span style={{ color: '#999' }}>-</span>
                      )}
                    </td>
                    <td>{new Date(scan.created_at).toLocaleDateString()}</td>
                    <td>
                      {scan.reviewed_at
                        ? new Date(scan.reviewed_at).toLocaleDateString()
                        : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="alert alert-info">
            No uploads yet. Start by <a href="/staff/upload-scan" style={{ color: '#0066cc', textDecoration: 'underline' }}>uploading a scan</a>.
          </div>
        )}

        {scans.length > 0 && (
          <div className="card">
            <h2>How It Works</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
              <div style={{ padding: '15px', background: '#f9f9f9', borderRadius: '6px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#667eea' }}>1️⃣ Upload</h4>
                <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                  You upload retinal scan image for a patient
                </p>
              </div>
              <div style={{ padding: '15px', background: '#f9f9f9', borderRadius: '6px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#667eea' }}>2️⃣ AI Analysis</h4>
                <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                  AI model analyzes scan and provides grade (0-4)
                </p>
              </div>
              <div style={{ padding: '15px', background: '#f9f9f9', borderRadius: '6px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#667eea' }}>3️⃣ Doctor Review</h4>
                <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                  Doctor reviews and provides clinical assessment
                </p>
              </div>
              <div style={{ padding: '15px', background: '#f9f9f9', borderRadius: '6px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#667eea' }}>4️⃣ Results</h4>
                <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
                  Patient can view results and doctor's clinical notes
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
