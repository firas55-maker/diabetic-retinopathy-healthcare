import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Sidebar } from '../../components/Sidebar';
import api from '../../services/api';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export const StatsPage: React.FC = () => {
  const { email, role } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [hospitalStats, setHospitalStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'personal' | 'hospital'>('personal');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [personal, hospital] = await Promise.all([
        api.getDashboardStats(),
        api.getHospitalStats(),
      ]);
      setStats(personal);
      setHospitalStats(hospital);
    } catch (err) {
      console.error('Failed to load stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!email || !role) return <div>Loading...</div>;

  const currentStats = activeTab === 'personal' ? stats : hospitalStats;

  return (
    <div className="dashboard-container">
      <Sidebar role={role} email={email} />
      <div className="main-content">
        <div className="header">
          <h1>Statistics Dashboard</h1>
          <div className="user-info">
            <strong>{email}</strong>
            <p>Analytics & Insights</p>
          </div>
        </div>

        {loading ? (
          <div className="spinner"></div>
        ) : currentStats ? (
          <>
            {/* Tab Switcher */}
            <div className="card" style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  className={`btn ${activeTab === 'personal' ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setActiveTab('personal')}
                >
                  My Stats
                </button>
                <button
                  className={`btn ${activeTab === 'hospital' ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setActiveTab('hospital')}
                >
                  Hospital Average
                </button>
              </div>
            </div>

            {/* Statistics Cards */}
            <div className="grid-3">
              <div className="stat-card">
                <h3>Total Patients</h3>
                <div className="stat-card-value">{currentStats.total_patients}</div>
                <p className="stat-card-label">in hospital</p>
              </div>
              <div className="stat-card">
                <h3>Reviewed Scans</h3>
                <div className="stat-card-value">{currentStats.reviewed_scans_count}</div>
                <p className="stat-card-label">completed</p>
              </div>
              <div className="stat-card">
                <h3>DR Prevalence</h3>
                <div className="stat-card-value">{currentStats.affected_percentage.toFixed(1)}%</div>
                <p className="stat-card-label">{currentStats.affected_scans_count} affected</p>
              </div>
            </div>

            {/* Age Group Breakdown */}
            <div className="card">
              <h2>Age Group Breakdown (Affected Patients)</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={currentStats.age_group_breakdown}>
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
              <h2>Monthly Scan Volume</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={currentStats.monthly_scan_counts}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month_name" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#667eea" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* DR Prevalence Pie */}
            <div className="grid-2">
              <div className="card">
                <h2>DR Prevalence</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'With DR', value: currentStats.affected_scans_count },
                        { name: 'No DR', value: currentStats.reviewed_scans_count - currentStats.affected_scans_count }
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
                <h2>Age Distribution</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={currentStats.age_group_breakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ dataKey, value }: any) => {
                        const total = currentStats.age_group_breakdown.reduce((sum: number, item: any) => sum + item.count, 0);
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
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
};
