import React, { useState, useEffect } from 'react';
import { AppShell } from '../../components/AppShell';
import api from '../../services/api';

export const PatientPortal: React.FC = () => {
  const [patient, setPatient] = useState<any>(null);
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPatientData();
  }, []);

  const fetchPatientData = async () => {
    try {
      setLoading(true);
      // Get all patients and scans to construct patient view
      const patientsData = await api.getPatients();
      const scansData = await api.getScanQueue();

      if (patientsData && patientsData.length > 0) {
        // Use first patient as demo (in real app, this would be based on authentication)
        setPatient(patientsData[0]);
        // Filter scans for this patient
        const patientScans = scansData?.filter((s: any) => s.patient_code === patientsData[0].patient_code) || [];
        setScans(patientScans);
      }
    } catch (err: any) {
      console.error('Failed to load patient data:', err);
      setError('Unable to load your information');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityLabel = (grade: number) => {
    const labels = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative'];
    return labels[grade] || 'Unknown';
  };

  const getSeverityColor = (grade: number) => {
    if (grade === 0) return 'var(--severity-none)';
    if (grade === 1) return 'var(--severity-mild)';
    if (grade === 2) return 'var(--severity-moderate)';
    if (grade === 3) return 'var(--severity-severe)';
    return 'var(--severity-proliferative)';
  };

  if (loading) {
    return (
      <AppShell>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div className="spinner"></div>
          <p style={{ marginTop: '20px', color: 'var(--color-gray-600)' }}>Loading your information...</p>
        </div>
      </AppShell>
    );
  }

  if (!patient) {
    return (
      <AppShell>
        <div className="alert alert-error" style={{ marginBottom: '20px' }}>
          {error || 'Unable to load patient information'}
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="greeting">Welcome, {patient.full_name}</h1>
        <p className="greeting-subtext">Your retinal screening information</p>
      </div>

      {/* PATIENT OVERVIEW CARDS */}
      <div className="grid-3" style={{ marginBottom: 'var(--spacing-8)' }}>
        <div className="card">
          <div className="card-body" style={{ textAlign: 'center' }}>
            <p style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'bold', color: 'var(--color-primary)', margin: '0 0 var(--spacing-2) 0' }}>
              {scans.length}
            </p>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', margin: 0 }}>
              Screening Tests
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-body" style={{ textAlign: 'center' }}>
            <p style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'bold', color: 'var(--color-success)', margin: '0 0 var(--spacing-2) 0' }}>
              {scans.filter(s => s.status === 'reviewed').length}
            </p>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', margin: 0 }}>
              Completed
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-body" style={{ textAlign: 'center' }}>
            <p style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'bold', color: 'var(--color-warning)', margin: '0 0 var(--spacing-2) 0' }}>
              {scans.filter(s => s.status === 'pending_review').length}
            </p>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', margin: 0 }}>
              Pending Review
            </p>
          </div>
        </div>
      </div>

      {/* PATIENT INFORMATION */}
      <div className="grid-2" style={{ marginBottom: 'var(--spacing-8)' }}>
        <div className="card">
          <div className="card-header">
            <h3>Personal Information</h3>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gap: 'var(--spacing-4)' }}>
              <div>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>
                  Full Name
                </p>
                <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, margin: 0 }}>
                  {patient.full_name}
                </p>
              </div>
              <div>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>
                  Date of Birth
                </p>
                <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, margin: 0 }}>
                  {patient.date_of_birth || '-'}
                </p>
              </div>
              <div>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>
                  Patient Code
                </p>
                <code style={{ fontSize: 'var(--font-size-base)', color: 'var(--color-primary)' }}>
                  {patient.patient_code}
                </code>
              </div>
              <div>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>
                  Hospital
                </p>
                <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, margin: 0 }}>
                  {patient.hospital || '-'}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Latest Results</h3>
          </div>
          <div className="card-body">
            {scans.length > 0 ? (
              <div style={{ display: 'grid', gap: 'var(--spacing-4)' }}>
                {scans[0] && (
                  <>
                    <div>
                      <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-2)' }}>
                        Most Recent Test
                      </p>
                      <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, margin: 0 }}>
                        {new Date(scans[0].created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-2)' }}>
                        Result
                      </p>
                      {scans[0].status === 'reviewed' ? (
                        <span style={{
                          display: 'inline-block',
                          padding: 'var(--spacing-2) var(--spacing-3)',
                          borderRadius: 'var(--radius-md)',
                          backgroundColor: getSeverityColor(scans[0].ai_grade),
                          color: 'white',
                          fontSize: 'var(--font-size-sm)',
                          fontWeight: 'bold'
                        }}>
                          {getSeverityLabel(scans[0].ai_grade)}
                        </span>
                      ) : (
                        <span style={{ color: 'var(--color-gray-600)' }}>Pending review</span>
                      )}
                    </div>
                  </>
                )}
              </div>
            ) : (
              <p style={{ color: 'var(--color-gray-600)' }}>No screening results yet</p>
            )}
          </div>
        </div>
      </div>

      {/* SCREENING HISTORY */}
      <div className="card" style={{ marginBottom: 'var(--spacing-8)' }}>
        <div className="card-header">
          <h3>Screening History</h3>
        </div>
        <div className="card-body">
          {scans.length === 0 ? (
            <div className="empty-state">
              <p className="empty-state-icon">📋</p>
              <h3>No screening tests yet</h3>
              <p>Your screening results will appear here once tests are completed.</p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Result</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {scans.map((scan) => (
                  <tr key={scan.id}>
                    <td>{new Date(scan.created_at).toLocaleDateString()}</td>
                    <td>
                      <span style={{
                        display: 'inline-block',
                        padding: 'var(--spacing-1) var(--spacing-3)',
                        borderRadius: 'var(--radius-md)',
                        fontSize: 'var(--font-size-xs)',
                        fontWeight: 600,
                        backgroundColor: scan.status === 'reviewed' ? 'var(--status-reviewed)' : 'var(--status-pending)',
                        color: 'white'
                      }}>
                        {scan.status === 'reviewed' ? '✓ Reviewed' : '⏳ Pending'}
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
                        <span style={{ color: 'var(--color-gray-500)' }}>-</span>
                      )}
                    </td>
                    <td>
                      {scan.status === 'reviewed' && (
                        <span style={{ fontWeight: 500 }}>
                          {((scan.ai_confidence || 0) * 100).toFixed(0)}%
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* IMPORTANT INFORMATION */}
      <div className="card" style={{ marginBottom: 'var(--spacing-8)', borderLeft: '4px solid var(--color-warning)' }}>
        <div className="card-body">
          <div style={{ display: 'flex', gap: 'var(--spacing-4)', alignItems: 'flex-start' }}>
            <span style={{ fontSize: 'var(--font-size-2xl)', minWidth: '40px' }}>⚠️</span>
            <div>
              <h3 style={{ margin: '0 0 var(--spacing-2) 0' }}>Important Medical Information</h3>
              <ul style={{ margin: 0, paddingLeft: 'var(--spacing-5)', color: 'var(--color-gray-700)', lineHeight: 1.6 }}>
                <li>Regular screening is recommended for early detection of diabetic retinopathy</li>
                <li>If any abnormalities are detected, follow up with your healthcare provider immediately</li>
                <li>AI results are preliminary and must be reviewed by a qualified ophthalmologist</li>
                <li>Contact your hospital or clinic for detailed results and treatment recommendations</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
};
