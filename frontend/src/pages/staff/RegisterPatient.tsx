import React, { useState } from 'react';
import { AppShell } from '../../components/AppShell';
import api from '../../services/api';

export const RegisterPatient: React.FC = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    date_of_birth: '',
    sex: 'male',
    hospital_id: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setGeneratedCode('');

    if (!formData.full_name || !formData.date_of_birth || !formData.hospital_id) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      const response = await api.registerPatient({
        full_name: formData.full_name,
        date_of_birth: formData.date_of_birth,
        sex: formData.sex,
        hospital_id: formData.hospital_id,
      });

      if (response.patient_code) {
        setGeneratedCode(response.patient_code);
        setSuccess(true);
        setFormData({ full_name: '', date_of_birth: '', sex: 'male', hospital_id: '' });
      }
    } catch (err: any) {
      console.error('Failed to register patient:', err);
      setError(err.response?.data?.detail || 'Failed to register patient. Please check all fields and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-header-title">Register New Patient</h1>
        <p className="page-header-desc">Add a new patient to the screening database</p>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-6)' }}>{error}</div>}

      {success && generatedCode && (
        <div className="alert alert-success" style={{ marginBottom: 'var(--spacing-6)' }}>
          <div style={{ marginBottom: 'var(--spacing-3)' }}>
            <strong>✓ Patient registered successfully!</strong>
          </div>
          <div style={{ padding: 'var(--spacing-4)', backgroundColor: 'rgba(255, 255, 255, 0.2)', borderRadius: 'var(--radius-md)' }}>
            <p style={{ fontSize: 'var(--font-size-sm)', margin: '0 0 var(--spacing-2) 0', color: 'rgba(255, 255, 255, 0.8)' }}>Patient Code:</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-3)' }}>
              <code style={{ fontSize: 'var(--font-size-lg)', fontWeight: 'bold', flex: 1 }}>{generatedCode}</code>
              <button
                className="btn btn-sm"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                  border: 'none',
                  cursor: 'pointer',
                }}
                onClick={() => {
                  navigator.clipboard.writeText(generatedCode);
                }}
              >
                Copy
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h3>Patient Information</h3>
          </div>
          <form onSubmit={handleSubmit} className="card-body">
            <div style={{ display: 'grid', gap: 'var(--spacing-6)' }}>
              <div>
                <label style={{ display: 'block', marginBottom: 'var(--spacing-2)', fontWeight: 500, fontSize: 'var(--font-size-sm)' }}>
                  Full Name *
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  placeholder="Enter patient's full name"
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: 'var(--spacing-2)', fontWeight: 500, fontSize: 'var(--font-size-sm)' }}>
                  Date of Birth *
                </label>
                <input
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: 'var(--spacing-2)', fontWeight: 500, fontSize: 'var(--font-size-sm)' }}>
                  Sex
                </label>
                <select
                  name="sex"
                  value={formData.sex}
                  onChange={handleChange}
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: 'var(--spacing-2)', fontWeight: 500, fontSize: 'var(--font-size-sm)' }}>
                  Hospital ID *
                </label>
                <input
                  type="text"
                  name="hospital_id"
                  value={formData.hospital_id}
                  onChange={handleChange}
                  placeholder="Enter hospital UUID"
                  required
                />
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-600)', marginTop: 'var(--spacing-2)' }}>
                  The unique identifier for your hospital
                </p>
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-block"
                disabled={loading}
                style={{ marginTop: 'var(--spacing-4)' }}
              >
                {loading ? 'Registering...' : 'Register Patient'}
              </button>
            </div>
          </form>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Registration Info</h3>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gap: 'var(--spacing-6)' }}>
              <div>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-2)' }}>
                  What happens next?
                </p>
                <div style={{ display: 'grid', gap: 'var(--spacing-3)' }}>
                  <div style={{ display: 'flex', gap: 'var(--spacing-3)' }}>
                    <span style={{ fontSize: 'var(--font-size-xl)', minWidth: '32px' }}>1️⃣</span>
                    <div>
                      <p style={{ margin: 0, fontWeight: 500, marginBottom: 'var(--spacing-1)' }}>Patient Code Generated</p>
                      <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)' }}>
                        A unique code will be created for identification
                      </p>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 'var(--spacing-3)' }}>
                    <span style={{ fontSize: 'var(--font-size-xl)', minWidth: '32px' }}>2️⃣</span>
                    <div>
                      <p style={{ margin: 0, fontWeight: 500, marginBottom: 'var(--spacing-1)' }}>Ready for Scans</p>
                      <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)' }}>
                        Upload retinal scans using the patient code
                      </p>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 'var(--spacing-3)' }}>
                    <span style={{ fontSize: 'var(--font-size-xl)', minWidth: '32px' }}>3️⃣</span>
                    <div>
                      <p style={{ margin: 0, fontWeight: 500, marginBottom: 'var(--spacing-1)' }}>AI Processing</p>
                      <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)' }}>
                        Scans are analyzed by AI for diabetic retinopathy
                      </p>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 'var(--spacing-3)' }}>
                    <span style={{ fontSize: 'var(--font-size-xl)', minWidth: '32px' }}>4️⃣</span>
                    <div>
                      <p style={{ margin: 0, fontWeight: 500, marginBottom: 'var(--spacing-1)' }}>Doctor Review</p>
                      <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)' }}>
                        Doctors review AI results and make final diagnosis
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div style={{ padding: 'var(--spacing-4)', backgroundColor: 'var(--color-gray-50)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-gray-200)' }}>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-2)' }}>
                  ℹ️ Important
                </p>
                <p style={{ margin: 0, fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-700)' }}>
                  Ensure all patient information is accurate before registration. Patient codes cannot be changed after creation.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
};
