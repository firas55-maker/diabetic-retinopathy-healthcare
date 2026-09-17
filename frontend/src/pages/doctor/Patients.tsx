import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../../components/AppShell';
import api from '../../services/api';

export const DoctorPatients: React.FC = () => {
  const navigate = useNavigate();
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      const data = await api.getPatients();
      setPatients(data || []);
    } catch (err: any) {
      console.error('Failed to load patients:', err);
      setError('Unable to load patients');
    } finally {
      setLoading(false);
    }
  };

  const filteredPatients = patients.filter((p) =>
    p.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.patient_code?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const calculateAge = (dateOfBirth: string) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'reviewed':
        return 'reviewed';
      case 'pending_review':
        return 'pending';
      case 'pending':
      default:
        return 'pending';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'reviewed':
        return '✓ Reviewed';
      case 'pending_review':
        return '⏳ Pending Review';
      case 'pending':
      default:
        return '⏳ Pending';
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div className="spinner"></div>
          <p style={{ marginTop: '20px', color: 'var(--color-gray-600)' }}>Loading patients...</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-header-title">My Patients</h1>
        <p className="page-header-desc">Manage and review patients assigned to your care</p>
        <div className="page-header-actions">
          <input
            type="text"
            placeholder="Search by name or patient code..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              flex: 1,
              maxWidth: '400px',
              padding: 'var(--spacing-2) var(--spacing-4)',
              border: '1px solid var(--color-gray-300)',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-sm)'
            }}
          />
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-6)' }}>{error}</div>}

      <div className="card">
        {filteredPatients.length === 0 ? (
          <div className="empty-state">
            <p className="empty-state-icon">👥</p>
            <h3>No patients found</h3>
            <p>No patients match your search or you haven't been assigned any patients yet.</p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Patient</th>
                <th>Patient Code</th>
                <th>Age</th>
                <th>Scans</th>
                <th>Last Scan</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredPatients.map((patient) => (
                <tr key={patient.id}>
                  <td><strong>{patient.full_name}</strong></td>
                  <td><code style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-600)' }}>{patient.patient_code}</code></td>
                  <td>{calculateAge(patient.date_of_birth)} years</td>
                  <td>{patient.scans_count || 0}</td>
                  <td>{patient.last_scan ? new Date(patient.last_scan).toLocaleDateString() : '-'}</td>
                  <td>
                    <span className={`status-badge ${getStatusBadgeClass(patient.status)}`}>
                      {getStatusLabel(patient.status)}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => navigate(`/doctor/patients/${patient.id}`)}
                    >
                      View →
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
