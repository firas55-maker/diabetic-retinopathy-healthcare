import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Sidebar } from '../../components/Sidebar';
import api from '../../services/api';

export const MyPatients: React.FC = () => {
  const { email, role } = useAuth();
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const data = await api.getMyPatients();
      setPatients(data.patients || []);
    } catch (err) {
      console.error('Failed to load patients:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!email || !role) return <div>Loading...</div>;

  return (
    <div className="dashboard-container">
      <Sidebar role={role} email={email} />
      <div className="main-content">
        <div className="header">
          <h1>My Patients</h1>
          <div className="user-info">
            <strong>{email}</strong>
            <p>Total: {patients.length} patients</p>
          </div>
        </div>

        {loading ? (
          <div className="spinner"></div>
        ) : patients.length > 0 ? (
          <div className="card">
            <table className="table">
              <thead>
                <tr>
                  <th>Patient Code</th>
                  <th>Name</th>
                  <th>DOB</th>
                  <th>Scans</th>
                  <th>Latest Scan</th>
                  <th>Latest Grade</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((patient) => (
                  <tr key={patient.id}>
                    <td>{patient.patient_code}</td>
                    <td>{patient.full_name}</td>
                    <td>{patient.date_of_birth}</td>
                    <td>{patient.scan_count}</td>
                    <td>{patient.latest_scan_date ? new Date(patient.latest_scan_date).toLocaleDateString() : 'N/A'}</td>
                    <td>
                      {patient.latest_doctor_grade !== null ? (
                        <span className={`badge badge-${['success', 'warning', 'danger', 'danger'][patient.latest_doctor_grade] || 'info'}`}>
                          Grade {patient.latest_doctor_grade}
                        </span>
                      ) : (
                        <span className="badge badge-info">Pending</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="alert alert-info">No patients yet. Start reviewing scans to build your patient list.</div>
        )}
      </div>
    </div>
  );
};
