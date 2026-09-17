import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Sidebar } from '../components/Sidebar';
import api from '../services/api';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export const DoctorDashboard: React.FC = () => {
  const { email, role } = useAuth();
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
      setError('Failed to load dashboard statistics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!email || !role) {
    return <div>Loading...</div>;
  }

  return (
    <div className="dashboard-container">
      <Sidebar role={role} email={email} />
      <div className="main-content">
        <div className="header">
          <h1>Doctor Dashboard</h1>
          <div className="user-info">
            <strong>{email}</strong>
            <p>Role: Doctor</p>
          </div>
        </div>

        {loading ? (
          <div className="spinner"></div>
        ) : error ? (
          <div className="alert alert-error">{error}</div>
        ) : stats ? (
          <>
            {/* Statistics Cards */}
            <div className="grid-3">
              <div className="stat-card">
                <h3>Total Patients</h3>
                <div className="stat-card-value">{stats.total_patients}</div>
                <p className="stat-card-label">in your hospital</p>
              </div>
              <div className="stat-card">
                <h3>Reviewed Scans</h3>
                <div className="stat-card-value">{stats.reviewed_scans_count}</div>
                <p className="stat-card-label">completed reviews</p>
              </div>
              <div className="stat-card">
                <h3>Affected Patients</h3>
                <div className="stat-card-value">{stats.affected_percentage.toFixed(1)}%</div>
                <p className="stat-card-label">{stats.affected_scans_count} scans with DR</p>
              </div>
            </div>

            {/* Age Group Breakdown */}
            <div className="card">
              <h2>Age Group Breakdown (Affected Patients)</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.age_group_breakdown}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="group" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#667eea" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Monthly Trends */}
            <div className="card">
              <h2>Scan Volume Trend (Last 12 Months)</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats.monthly_scan_counts}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="month_name"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#667eea" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Affected vs Unaffected Pie Chart */}
            <div className="card">
              <h2>DR Prevalence</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'With DR', value: stats.affected_scans_count },
                      { name: 'No DR', value: stats.reviewed_scans_count - stats.affected_scans_count }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }: any) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    <Cell fill="#e74c3c" />
                    <Cell fill="#27ae60" />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Age Distribution */}
            <div className="card">
              <h2>Age Group Distribution</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={stats.age_group_breakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ dataKey, value }: any) => {
                      const total = stats.age_group_breakdown.reduce((sum: number, item: any) => sum + item.count, 0);
                      const percent = ((value / total) * 100).toFixed(0);
                      return `${percent}%`;
                    }}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    <Cell fill="#667eea" />
                    <Cell fill="#764ba2" />
                    <Cell fill="#f39c12" />
                    <Cell fill="#e74c3c" />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
};
