import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../../components/AppShell';
import api from '../../services/api';

const formatScanDate = (dateString: string | undefined): string => {
  if (!dateString) return 'Invalid Date';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Invalid Date';
    }
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch (e) {
    return 'Invalid Date';
  }
};

export const ScanQueue: React.FC = () => {
  const navigate = useNavigate();
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<'all' | 'pending' | 'reviewed'>('pending');

  useEffect(() => {
    fetchScans();
  }, []);

  const fetchScans = async () => {
    try {
      setLoading(true);
      const response = await api.getScanQueue();
      console.log('Raw API response:', response);
      // API returns { scans: [...], total: N }, extract the scans array
      const scansArray = response?.scans || [];
      setScans(scansArray);
    } catch (err: any) {
      console.error('Failed to load scan queue:', err);
      setError('Unable to load scan queue');
      setScans([]); // Ensure scans is always an array, never undefined
    } finally {
      setLoading(false);
    }
  };

  const filteredScans = scans.filter((scan) => {
    if (filter === 'all') return true;
    if (filter === 'pending') return scan.status === 'pending_review';
    if (filter === 'reviewed') return scan.status === 'reviewed';
    return true;
  });

  const getSeverityColor = (grade: number) => {
    if (grade === 0) return 'var(--severity-none)';
    if (grade === 1) return 'var(--severity-mild)';
    if (grade === 2) return 'var(--severity-moderate)';
    if (grade === 3) return 'var(--severity-severe)';
    return 'var(--severity-proliferative)';
  };

  const getSeverityLabel = (grade: number) => {
    const labels = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative'];
    return labels[grade] || 'Unknown';
  };

  if (loading) {
    return (
      <AppShell>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div className="spinner"></div>
          <p style={{ marginTop: '20px', color: 'var(--color-gray-600)' }}>Loading scan queue...</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-header-title">Scan Queue</h1>
        <p className="page-header-desc">Retinal scans awaiting medical review</p>

        <div className="page-header-actions" style={{ gap: 'var(--spacing-2)' }}>
          {(['all', 'pending', 'reviewed'] as const).map((f) => (
            <button
              key={f}
              className={`btn ${filter === f ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilter(f)}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-6)' }}>{error}</div>}

      <div className="card">
        {filteredScans.length === 0 ? (
          <div className="empty-state">
            <p className="empty-state-icon">✅</p>
            <h3>
              {filter === 'pending' ? 'No pending reviews' : 'No scans found'}
            </h3>
            <p>
              {filter === 'pending'
                ? 'All available screening cases have been reviewed.'
                : 'No scans match the selected filter.'}
            </p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Patient</th>
                <th>Patient Code</th>
                <th>Scan Date</th>
                <th>AI Result</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredScans.map((scan) => (
                <tr key={scan.id} style={{
                  backgroundColor: scan.status === 'pending_review' ? 'rgba(234, 88, 12, 0.05)' : 'transparent'
                }}>
                  <td><strong>{scan.patient_name || 'Unknown'}</strong></td>
                  <td><code style={{ fontSize: 'var(--font-size-xs)' }}>{scan.patient_code}</code></td>
                  <td>{formatScanDate(scan.created_at)}</td>
                  <td>
                    <span style={{
                      display: 'inline-block',
                      padding: 'var(--spacing-1) var(--spacing-3)',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: getSeverityColor(scan.ai_grade),
                      color: 'white',
                      fontSize: 'var(--font-size-sm)',
                      fontWeight: 500
                    }}>
                      {getSeverityLabel(scan.ai_grade)}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
                      <div style={{ width: '100%', height: '6px', backgroundColor: 'var(--color-gray-200)', borderRadius: 'var(--radius-full)' }}>
                        <div style={{
                          height: '100%',
                          width: `${(scan.ai_confidence || 0) * 100}%`,
                          backgroundColor: 'var(--color-success)',
                          borderRadius: 'var(--radius-full)',
                          transition: 'width 0.3s'
                        }} />
                      </div>
                      <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500 }}>
                        {((scan.ai_confidence || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className={`status-badge ${scan.status === 'pending_review' ? 'pending' : 'reviewed'}`}>
                      {scan.status === 'pending_review' ? '⏳ Pending' : '✓ Reviewed'}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => navigate(`/doctor/scan/${scan.id}`)}
                    >
                      Review →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </AppShell>
  );
};
