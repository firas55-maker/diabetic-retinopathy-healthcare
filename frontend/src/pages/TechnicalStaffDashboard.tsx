import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Sidebar } from '../components/Sidebar';
import api from '../services/api';

export const TechnicalStaffDashboard: React.FC = () => {
  const { email, role } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await api.getMyScans(0, 100);
      setStats(data);
    } catch (err) {
      console.error('Failed to load scans:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!email || !role) return <div>Loading...</div>;

  const getStatusSummary = () => {
    if (!stats) return { pending: 0, reviewed: 0, total: 0 };
    const scans = stats.scans || [];
    return {
      total: scans.length,
      pending: scans.filter((s: any) => s.status === 'pending_review').length,
      reviewed: scans.filter((s: any) => s.status === 'reviewed').length,
    };
  };

  const summary = getStatusSummary();

  return (
    <div className="dashboard-container">
      <Sidebar role={role} email={email} />
      <div className="main-content">
        <div className="header">
          <h1>Technical Staff Dashboard</h1>
          <div className="user-info">
            <strong>{email}</strong>
            <p>Role: Technical Staff</p>
          </div>
        </div>

        {loading ? (
          <div className="spinner"></div>
        ) : (
          <>
            {/* Quick Stats */}
            <div className="grid-3">
              <div className="stat-card">
                <h3>Total Uploads</h3>
                <div className="stat-card-value">{summary.total}</div>
                <p className="stat-card-label">scans uploaded</p>
              </div>
              <div className="stat-card">
                <h3>Pending Review</h3>
                <div className="stat-card-value">{summary.pending}</div>
                <p className="stat-card-label">awaiting doctor review</p>
              </div>
              <div className="stat-card">
                <h3>Reviewed</h3>
                <div className="stat-card-value">{summary.reviewed}</div>
                <p className="stat-card-label">completed reviews</p>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
              <h2>Quick Actions</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
                <a href="/staff/register-patient" className="btn btn-primary" style={{ textAlign: 'center', textDecoration: 'none', display: 'block', padding: '15px' }}>
                  ➕ Register New Patient
                </a>
                <a href="/staff/upload-scan" className="btn btn-primary" style={{ textAlign: 'center', textDecoration: 'none', display: 'block', padding: '15px' }}>
                  📸 Upload Scan
                </a>
                <a href="/staff/my-uploads" className="btn btn-secondary" style={{ textAlign: 'center', textDecoration: 'none', display: 'block', padding: '15px' }}>
                  📋 View My Uploads
                </a>
              </div>
            </div>

            {/* Recent Uploads */}
            {stats?.scans && stats.scans.length > 0 && (
              <div className="card">
                <h2>Recent Uploads</h2>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Patient Code</th>
                      <th>AI Grade</th>
                      <th>Status</th>
                      <th>Uploaded</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.scans.slice(0, 5).map((scan: any) => (
                      <tr key={scan.id}>
                        <td>{scan.patient_code}</td>
                        <td>{scan.ai_grade} ({scan.ai_severity})</td>
                        <td>
                          <span className={`badge badge-${scan.status === 'pending_review' ? 'pending' : 'reviewed'}`}>
                            {scan.status}
                          </span>
                        </td>
                        <td>{new Date(scan.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
