import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppShell } from '../../components/AppShell';
import api from '../../services/api';

export const PatientDetails: React.FC = () => {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState<any>(null);
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPatientData();
  }, [patientId]);

  const fetchPatientData = async () => {
    try {
      setLoading(true);
      // Get patient from patients list as fallback
      const patientsData = await api.getPatients();
      const patientData = patientsData?.find((p: any) => p.id === patientId);
      if (patientData) {
        setPatient(patientData);
      }
    } catch (err: any) {
      console.error('Failed to load patient:', err);
      setError('Unable to load patient details');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div className="spinner"></div>
        </div>
      </AppShell>
    );
  }

  if (!patient) {
    return (
      <AppShell>
        <button className="btn btn-ghost" onClick={() => navigate('/doctor/patients')} style={{ marginBottom: 'var(--spacing-4)' }}>
          ← Back to Patients
        </button>
        <div className="alert alert-error">Patient not found</div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <button className="btn btn-ghost" onClick={() => navigate('/doctor/patients')} style={{ marginBottom: 'var(--spacing-4)' }}>
        ← Back to Patients
      </button>

      <div className="page-header" style={{ marginBottom: 'var(--spacing-6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)', marginBottom: 'var(--spacing-4)' }}>
          <h1 className="page-header-title" style={{ margin: 0 }}>{patient.full_name}</h1>
          <span className="badge badge-success">Active</span>
        </div>
        <p className="page-header-desc" style={{ marginBottom: 'var(--spacing-2)' }}>
          <code>{patient.patient_code}</code>
        </p>
      </div>

      <div className="grid-2" style={{ marginBottom: 'var(--spacing-8)' }}>
        <div className="card">
          <div className="card-header">
            <h3>Patient Information</h3>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gap: 'var(--spacing-4)' }}>
              <div>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>Date of Birth</p>
                <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 500 }}>{patient.date_of_birth || '-'}</p>
              </div>
              <div>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>Sex</p>
                <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, textTransform: 'capitalize' }}>{patient.sex || '-'}</p>
              </div>
              <div>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>Hospital</p>
                <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 500 }}>{patient.hospital || '-'}</p>
              </div>
              <div>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>Registered</p>
                <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 500 }}>
                  {patient.created_at ? new Date(patient.created_at).toLocaleDateString() : '-'}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Screening Summary</h3>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gap: 'var(--spacing-6)', textAlign: 'center' }}>
              <div>
                <p style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'bold', color: 'var(--color-primary)', margin: 0 }}>
                  {patient.scan_count || 0}
                </p>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', margin: 0 }}>Total Scans</p>
              </div>
              <div>
                <p style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'bold', margin: 0 }}>
                  {patient.latest_ai_grade !== null && patient.latest_ai_grade !== undefined ? patient.latest_ai_grade : '-'}
                </p>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', margin: 0 }}>Latest AI Grade</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 'var(--spacing-8)' }}>
        <div className="card-header">
          <h3>Screening History</h3>
        </div>
        <div className="card-body">
          <div className="empty-state">
            <p>📋 Scan history will appear here</p>
            <p style={{ fontSize: 'var(--font-size-sm)' }}>Once scans are uploaded, they will be listed below</p>
          </div>
        </div>
      </div>
    </AppShell>
  );
};
