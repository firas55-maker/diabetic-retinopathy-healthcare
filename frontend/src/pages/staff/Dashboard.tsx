import React, { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import api from '../../services/api';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const StaffDashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      console.error('Failed to load staff dashboard:', err);
      setError('Unable to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div className="spinner"></div>
          <p style={{ marginTop: '20px', color: 'var(--color-gray-600)' }}>Loading dashboard...</p>
        </div>
      </AppShell>
    );
  }

  if (error || !stats) {
    return (
      <AppShell>
        <div className="alert alert-error" style={{ marginBottom: '20px' }}>
          {error || 'Failed to load dashboard data'}
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="greeting">Operations Dashboard</h1>
        <p className="greeting-subtext">Manage patient registrations and scan uploads</p>
      </div>

      {/* KPI CARDS */}
      <div className="grid-4">
        <div className="stat-card">
          <h3>Total Patients</h3>
          <div className="stat-card-value">{stats.total_patients || 0}</div>
          <p className="stat-card-label">Registered in system</p>
        </div>

        <div className="stat-card">
          <h3>Total Scans</h3>
          <div className="stat-card-value">{stats.reviewed_scans_count || 0}</div>
          <p className="stat-card-label">Uploaded and processed</p>
        </div>

        <div className="stat-card">
          <h3>Pending Review</h3>
          <div className="stat-card-value" style={{ color: 'var(--status-pending)' }}>
            {stats.pending_reviews_count || 0}
          </div>
          <p className="stat-card-label">Awaiting doctor review</p>
        </div>

        <div className="stat-card">
          <h3>DR Cases</h3>
          <div className="stat-card-value" style={{ color: 'var(--color-warning)' }}>
            {stats.affected_scans_count || 0}
          </div>
          <p className="stat-card-label">Diabetic retinopathy detected</p>
        </div>
      </div>

      {/* CHARTS */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h2>Monthly Uploads</h2>
          </div>
          <div className="card-body">
            {stats.monthly_scan_counts && stats.monthly_scan_counts.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.monthly_scan_counts}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-gray-200)" />
                  <XAxis dataKey="month_name" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--color-white)',
                      border: '1px solid var(--color-gray-200)',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="count" fill="var(--color-primary)" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                <p>No upload data available</p>
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2>System Overview</h2>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gap: 'var(--spacing-4)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 'var(--spacing-4)', borderBottom: '1px solid var(--color-gray-200)' }}>
                <span style={{ color: 'var(--color-gray-600)' }}>Registration Success Rate</span>
                <strong>{stats.total_patients > 0 ? '100%' : '-'}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 'var(--spacing-4)', borderBottom: '1px solid var(--color-gray-200)' }}>
                <span style={{ color: 'var(--color-gray-600)' }}>Scans Processed</span>
                <strong>{stats.reviewed_scans_count || 0}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 'var(--spacing-4)', borderBottom: '1px solid var(--color-gray-200)' }}>
                <span style={{ color: 'var(--color-gray-600)' }}>DR Detection Rate</span>
                <strong>
                  {stats.reviewed_scans_count > 0
                    ? `${((stats.affected_scans_count || 0) / (stats.reviewed_scans_count || 1) * 100).toFixed(1)}%`
                    : '-'}
                </strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--color-gray-600)' }}>Pending Reviews</span>
                <strong>{stats.pending_reviews_count || 0}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* QUICK ACTIONS */}
      <div className="card" style={{ marginTop: 'var(--spacing-8)', marginBottom: 'var(--spacing-8)' }}>
        <div className="card-header">
          <h2>Quick Actions</h2>
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-4)' }}>
            <button className="btn btn-primary btn-block" style={{ height: 'auto', padding: 'var(--spacing-4)' }}>
              <span style={{ display: 'block', fontSize: 'var(--font-size-lg)', marginBottom: 'var(--spacing-2)' }}>➕</span>
              Register New Patient
            </button>
            <button className="btn btn-primary btn-block" style={{ height: 'auto', padding: 'var(--spacing-4)' }}>
              <span style={{ display: 'block', fontSize: 'var(--font-size-lg)', marginBottom: 'var(--spacing-2)' }}>📤</span>
              Upload Scan
            </button>
            <button className="btn btn-secondary btn-block" style={{ height: 'auto', padding: 'var(--spacing-4)' }}>
              <span style={{ display: 'block', fontSize: 'var(--font-size-lg)', marginBottom: 'var(--spacing-2)' }}>📋</span>
              View Upload History
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
};
