import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../../components/AppShell';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export const DoctorDashboard: React.FC = () => {
  const { email } = useAuth();
  const navigate = useNavigate();
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
      console.error('Failed to load dashboard:', err);
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

  // Extract doctor's first name for greeting
  const firstName = email?.split('@')[0] || 'Doctor';

  // Color palette for charts
  const chartColors = ['#1e7bcb', '#16a34a', '#ea580c', '#dc2626'];

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="greeting">Good morning, {firstName}</h1>
        <p className="greeting-subtext">Here's an overview of your retinal screening activity</p>
      </div>

      {/* KPI CARDS */}
      <div className="grid-4">
        <div className="stat-card">
          <h3>Total Patients</h3>
          <div className="stat-card-value">{stats.total_patients || 0}</div>
          <p className="stat-card-label">In your hospital</p>
        </div>

        <div className="stat-card">
          <h3>Pending Reviews</h3>
          <div className="stat-card-value" style={{ color: 'var(--status-pending)' }}>
            {stats.pending_reviews_count || 0}
          </div>
          <p className="stat-card-label">Requires attention</p>
        </div>

        <div className="stat-card">
          <h3>Reviewed Scans</h3>
          <div className="stat-card-value" style={{ color: 'var(--status-reviewed)' }}>
            {stats.reviewed_scans_count || 0}
          </div>
          <p className="stat-card-label">This month</p>
        </div>

        <div className="stat-card">
          <h3>Patients Requiring Follow-up</h3>
          <div className="stat-card-value" style={{ color: 'var(--color-warning)' }}>
            {stats.affected_scans_count || 0}
          </div>
          <p className="stat-card-label">DR detected</p>
        </div>
      </div>

      {/* CHARTS */}
      <div className="grid-2">
        {/* Activity Chart */}
        <div className="card">
          <div className="card-header">
            <h2>Screening Activity</h2>
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
                <p>No activity data available</p>
              </div>
            )}
          </div>
        </div>

        {/* DR Prevalence */}
        <div className="card">
          <div className="card-header">
            <h2>Cases by Severity</h2>
          </div>
          <div className="card-body">
            {stats.reviewed_scans_count > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'With DR', value: stats.affected_scans_count || 0 },
                      { name: 'No DR', value: (stats.reviewed_scans_count || 0) - (stats.affected_scans_count || 0) }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }: any) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="var(--color-primary)"
                    dataKey="value"
                  >
                    <Cell fill="var(--status-failed)" />
                    <Cell fill="var(--status-reviewed)" />
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--color-white)',
                      border: '1px solid var(--color-gray-200)',
                      borderRadius: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                <p>No review data available</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* RECENT CASES TABLE */}
      <div className="card" style={{ marginTop: 'var(--spacing-8)' }}>
        <div className="card-header">
          <h2>Recent Screening Cases</h2>
        </div>
        <div className="card-body">
          <div className="empty-state">
            <p>📋 Scan queue will appear here</p>
            <p style={{ fontSize: 'var(--font-size-sm)' }}>Navigate to "Scan Queue" to review pending cases</p>
            <button
              className="btn btn-primary"
              onClick={() => navigate('/doctor/queue')}
              style={{ marginTop: 'var(--spacing-4)' }}
            >
              Go to Scan Queue →
            </button>
          </div>
        </div>
      </div>

      {/* CASES REQUIRING ATTENTION */}
      <div className="card" style={{ marginTop: 'var(--spacing-8)', marginBottom: 'var(--spacing-8)' }}>
        <div className="card-header">
          <h2>Cases Requiring Attention</h2>
        </div>
        <div className="card-body">
          <div className="empty-state">
            <p>✅ No pending reviews</p>
            <p style={{ fontSize: 'var(--font-size-sm)' }}>All available screening cases have been reviewed.</p>
          </div>
        </div>
      </div>
    </AppShell>
  );
};
