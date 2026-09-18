import React, { useState, useEffect } from 'react';
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

export const UploadHistory: React.FC = () => {
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<'all' | 'pending' | 'processed'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchScans();
  }, []);

  const fetchScans = async () => {
    try {
      setLoading(true);
      const data = await api.getScanQueue();
      setScans(data?.scans || []);
    } catch (err: any) {
      console.error('Failed to load upload history:', err);
      setError('Unable to load upload history');
    } finally {
      setLoading(false);
    }
  };

  const filteredScans = scans
    .filter((scan) => {
      if (filter === 'pending') return scan.status === 'pending_review';
      if (filter === 'processed') return scan.status === 'reviewed';
      return true;
    })
    .filter((scan) =>
      scan.patient_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      scan.patient_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

  const getStatusColor = (status: string) => {
    if (status === 'pending_review') return 'var(--status-pending)';
    if (status === 'reviewed') return 'var(--status-reviewed)';
    return 'var(--color-gray-500)';
  };

  const getStatusLabel = (status: string) => {
    if (status === 'pending_review') return '⏳ Pending Review';
    if (status === 'reviewed') return '✓ Reviewed';
    return 'Unknown';
  };

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
          <p style={{ marginTop: '20px', color: 'var(--color-gray-600)' }}>Loading upload history...</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-header-title">Upload History</h1>
        <p className="page-header-desc">Track and manage all uploaded retinal scans</p>

        <div className="page-header-actions" style={{ gap: 'var(--spacing-2)', display: 'flex', alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            type="text"
            placeholder="Search by patient code or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              padding: 'var(--spacing-2) var(--spacing-4)',
              border: '1px solid var(--color-gray-300)',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-sm)',
              minWidth: '250px',
              flex: 1
            }}
          />
          <div style={{ display: 'flex', gap: 'var(--spacing-2)' }}>
            {(['all', 'pending', 'processed'] as const).map((f) => (
              <button
                key={f}
                className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setFilter(f)}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-6)' }}>{error}</div>}

      <div className="card">
        {filteredScans.length === 0 ? (
          <div className="empty-state">
            <p className="empty-state-icon">📋</p>
            <h3>
              {filter === 'all' && searchTerm ? 'No scans found' : filter === 'pending' ? 'No pending scans' : 'No processed scans'}
            </h3>
            <p>
              {filter === 'all' && searchTerm
                ? 'No scans match your search'
                : filter === 'pending'
                ? 'All uploaded scans have been reviewed'
                : 'No scans have been processed yet'}
            </p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Patient Code</th>
                <th>Patient Name</th>
                <th>Upload Date</th>
                <th>Status</th>
                <th>AI Result</th>
                <th>Confidence</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredScans.map((scan) => (
                <tr key={scan.id} style={{
                  backgroundColor: scan.status === 'pending_review' ? 'rgba(234, 88, 12, 0.05)' : 'transparent'
                }}>
                  <td>
                    <code style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-600)' }}>
                      {scan.patient_code}
                    </code>
                  </td>
                  <td><strong>{scan.patient_name || 'Unknown'}</strong></td>
                  <td>{formatScanDate(scan.created_at)}</td>
                  <td>
                    <span style={{
                      display: 'inline-block',
                      padding: 'var(--spacing-1) var(--spacing-3)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--font-size-xs)',
                      fontWeight: 600,
                      backgroundColor: getStatusColor(scan.status),
                      color: 'white'
                    }}>
                      {getStatusLabel(scan.status)}
                    </span>
                  </td>
                  <td>
                    {scan.status === 'reviewed' ? (
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
                    ) : (
                      <span style={{ color: 'var(--color-gray-500)', fontSize: 'var(--font-size-sm)' }}>-</span>
                    )}
                  </td>
                  <td>
                    {scan.status === 'reviewed' && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
                        <div style={{ width: '60px', height: '6px', backgroundColor: 'var(--color-gray-200)', borderRadius: 'var(--radius-full)' }}>
                          <div style={{
                            height: '100%',
                            width: `${(scan.ai_confidence || 0) * 100}%`,
                            backgroundColor: 'var(--color-success)',
                            borderRadius: 'var(--radius-full)'
                          }} />
                        </div>
                        <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 500, minWidth: '30px' }}>
                          {((scan.ai_confidence || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </td>
                  <td>
                    <button
                      className="btn btn-sm btn-ghost"
                      onClick={() => alert(`Scan ID: ${scan.id}`)}
                      title={`View details for scan ${scan.id}`}
                    >
                      Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {filteredScans.length > 0 && (
          <div className="card-footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)' }}>
            <span>Showing {filteredScans.length} scan{filteredScans.length !== 1 ? 's' : ''}</span>
            <span>
              Pending: {scans.filter(s => s.status === 'pending_review').length} |
              Processed: {scans.filter(s => s.status === 'reviewed').length}
            </span>
          </div>
        )}
      </div>
    </AppShell>
  );
};
