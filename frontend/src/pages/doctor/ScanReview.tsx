import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppShell } from '../../components/AppShell';
import api from '../../services/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const ScanReview: React.FC = () => {
  const { scanId } = useParams();
  const navigate = useNavigate();
  const [scan, setScan] = useState<any>(null);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [doctorGrade, setDoctorGrade] = useState<number | ''>('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchScan();
  }, [scanId]);

  const fetchScan = async () => {
    try {
      setLoading(true);
      // Fetch the specific scan detail with image data
      const scanDetail = await api.getScanDetail(scanId!);
      if (scanDetail) {
        setScan(scanDetail);
        // Pre-fill with AI grade as suggestion
        if (scanDetail.ai_grade !== undefined && scanDetail.ai_grade !== null) {
          setDoctorGrade(scanDetail.ai_grade);
        }
        // Fetch the image
        await fetchScanImage(scanId!);
      } else {
        setError('Scan not found');
      }
    } catch (err: any) {
      console.error('Failed to load scan:', err);
      setError('Unable to load scan details');
    } finally {
      setLoading(false);
    }
  };

  const fetchScanImage = async (scanId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/doctor/scans/${scanId}/image`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setImageUrl(url);
      } else {
        console.error('Failed to fetch image:', response.status);
      }
    } catch (err: any) {
      console.error('Error fetching image:', err);
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (doctorGrade === '') {
      setError('Please select a final grade');
      return;
    }

    try {
      setSubmitting(true);
      setError('');
      await api.submitScanReview(scanId!, {
        doctor_grade: doctorGrade,
        notes: notes,
      });
      setSuccess(true);
      setTimeout(() => {
        navigate('/doctor/queue');
      }, 2000);
    } catch (err: any) {
      console.error('Failed to submit review:', err);

      // Extract error message from response
      let errorMessage = 'Failed to submit review';

      if (err.response?.data) {
        const data = err.response.data;

        // Handle Pydantic validation errors (422)
        if (Array.isArray(data.detail)) {
          const errors = data.detail.map((e: any) => {
            if (typeof e === 'object' && e.msg) {
              const field = e.loc?.[1] || 'field';
              return `${field}: ${e.msg}`;
            }
            return String(e);
          });
          errorMessage = errors.join('; ');
        }
        // Handle regular error detail
        else if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        }
        // Handle object error detail
        else if (typeof data.detail === 'object' && data.detail?.msg) {
          errorMessage = data.detail.msg;
        }
      }

      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
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

  const gradeDescriptions: { [key: number]: string } = {
    0: 'No signs of diabetic retinopathy detected',
    1: 'Mild nonproliferative DR with microaneurysms only',
    2: 'Moderate nonproliferative DR with retinal hemorrhages and hard exudates',
    3: 'Severe nonproliferative DR with venous beading and intraretinal microvascular abnormalities',
    4: 'Proliferative DR with neovascularization',
  };

  if (loading) {
    return (
      <AppShell>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div className="spinner"></div>
          <p style={{ marginTop: '20px', color: 'var(--color-gray-600)' }}>Loading scan...</p>
        </div>
      </AppShell>
    );
  }

  if (!scan) {
    return (
      <AppShell>
        <button className="btn btn-ghost" onClick={() => navigate('/doctor/queue')} style={{ marginBottom: 'var(--spacing-4)' }}>
          ← Back to Queue
        </button>
        <div className="alert alert-error">{error || 'Scan not found'}</div>
      </AppShell>
    );
  }

  if (success) {
    return (
      <AppShell>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <p style={{ fontSize: 'var(--font-size-4xl)', margin: 0 }}>✅</p>
          <h2 style={{ marginTop: 'var(--spacing-4)', marginBottom: 'var(--spacing-2)' }}>Review Submitted</h2>
          <p style={{ color: 'var(--color-gray-600)', marginBottom: 'var(--spacing-6)' }}>
            Your assessment has been saved. Redirecting...
          </p>
          <button className="btn btn-primary" onClick={() => navigate('/doctor/queue')}>
            Return to Queue
          </button>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <button className="btn btn-ghost" onClick={() => navigate('/doctor/queue')} style={{ marginBottom: 'var(--spacing-6)' }}>
        ← Back to Queue
      </button>

      <div className="page-header" style={{ marginBottom: 'var(--spacing-6)' }}>
        <h1 className="page-header-title">Scan Review</h1>
        <p className="page-header-desc">
          Patient: <strong>{scan.patient_name}</strong> ({scan.patient_code})
        </p>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-6)' }}>{error}</div>}

      <div className="grid-2" style={{ gap: 'var(--spacing-6)' }}>
        {/* LEFT COLUMN - SCAN & AI RESULT */}
        <div>
          {/* SCAN IMAGE PLACEHOLDER */}
          <div className="card" style={{ marginBottom: 'var(--spacing-6)' }}>
            <div className="card-header">
              <h3>Retinal Scan Image</h3>
            </div>
            <div className="card-body">
              {imageUrl ? (
                <div style={{ position: 'relative' }}>
                  <img
                    src={imageUrl}
                    alt="Retinal scan"
                    style={{
                      width: '100%',
                      borderRadius: 'var(--radius-md)',
                      display: 'block',
                      backgroundColor: 'var(--color-gray-100)'
                    }}
                  />
                </div>
              ) : (
                <div style={{
                  backgroundColor: 'var(--color-gray-200)',
                  borderRadius: 'var(--radius-md)',
                  aspectRatio: '1',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-gray-600)',
                  fontSize: 'var(--font-size-4xl)'
                }}>
                  ⚠️ Image not available
                </div>
              )}
              <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-600)', marginTop: 'var(--spacing-3)', marginBottom: 0 }}>
                Uploaded: {new Date(scan.created_at).toLocaleString()}
              </p>
            </div>
          </div>

          {/* AI ANALYSIS */}
          <div className="card">
            <div className="card-header">
              <h3>AI Analysis Results</h3>
            </div>
            <div className="card-body">
              <div style={{ display: 'grid', gap: 'var(--spacing-6)' }}>
                <div>
                  <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-2)' }}>
                    Predicted Grade
                  </p>
                  <div style={{
                    display: 'inline-block',
                    padding: 'var(--spacing-2) var(--spacing-4)',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: getSeverityColor(scan.ai_grade),
                    color: 'white',
                    fontSize: 'var(--font-size-lg)',
                    fontWeight: 'bold'
                  }}>
                    {getSeverityLabel(scan.ai_grade)}
                  </div>
                  <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', marginTop: 'var(--spacing-2)', margin: 0 }}>
                    {gradeDescriptions[scan.ai_grade]}
                  </p>
                </div>

                <div style={{ borderTop: '1px solid var(--color-gray-200)', paddingTop: 'var(--spacing-4)' }}>
                  <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-2)' }}>
                    Model Confidence
                  </p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-3)' }}>
                    <div style={{ flex: 1, height: '8px', backgroundColor: 'var(--color-gray-200)', borderRadius: 'var(--radius-full)' }}>
                      <div style={{
                        height: '100%',
                        width: `${(scan.ai_confidence || 0) * 100}%`,
                        backgroundColor: 'var(--color-success)',
                        borderRadius: 'var(--radius-full)'
                      }} />
                    </div>
                    <span style={{ fontSize: 'var(--font-size-base)', fontWeight: 'bold', minWidth: '50px' }}>
                      {((scan.ai_confidence || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN - DOCTOR ASSESSMENT */}
        <form onSubmit={handleSubmitReview}>
          {/* PATIENT INFO */}
          <div className="card" style={{ marginBottom: 'var(--spacing-6)' }}>
            <div className="card-header">
              <h3>Patient Information</h3>
            </div>
            <div className="card-body">
              <div style={{ display: 'grid', gap: 'var(--spacing-4)' }}>
                <div>
                  <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>
                    Name
                  </p>
                  <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, margin: 0 }}>
                    {scan.patient_name}
                  </p>
                </div>
                <div>
                  <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>
                    Patient Code
                  </p>
                  <code style={{ fontSize: 'var(--font-size-base)' }}>{scan.patient_code}</code>
                </div>
                <div>
                  <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-500)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>
                    Scan Date
                  </p>
                  <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, margin: 0 }}>
                    {new Date(scan.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* DOCTOR GRADE SELECTION */}
          <div className="card" style={{ marginBottom: 'var(--spacing-6)' }}>
            <div className="card-header">
              <h3>Your Assessment</h3>
            </div>
            <div className="card-body">
              <div style={{ display: 'grid', gap: 'var(--spacing-4)' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: 'var(--spacing-3)', fontWeight: 600, fontSize: 'var(--font-size-base)' }}>
                    Final DR Grade *
                  </label>
                  <div style={{ display: 'grid', gap: 'var(--spacing-3)' }}>
                    {[0, 1, 2, 3, 4].map((grade) => (
                      <label key={grade} style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 'var(--spacing-3)',
                        padding: 'var(--spacing-3)',
                        borderRadius: 'var(--radius-md)',
                        border: `2px solid ${doctorGrade === grade ? 'var(--color-primary)' : 'var(--color-gray-200)'}`,
                        backgroundColor: doctorGrade === grade ? 'rgba(30, 123, 203, 0.05)' : 'transparent',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}>
                        <input
                          type="radio"
                          name="doctorGrade"
                          value={grade}
                          checked={doctorGrade === grade}
                          onChange={(e) => setDoctorGrade(parseInt(e.target.value))}
                          style={{ marginTop: '2px' }}
                        />
                        <div style={{ flex: 1 }}>
                          <div style={{
                            display: 'inline-block',
                            padding: 'var(--spacing-1) var(--spacing-2)',
                            borderRadius: 'var(--radius-md)',
                            backgroundColor: getSeverityColor(grade),
                            color: 'white',
                            fontSize: 'var(--font-size-xs)',
                            fontWeight: 'bold',
                            marginBottom: 'var(--spacing-1)'
                          }}>
                            {getSeverityLabel(grade)}
                          </div>
                          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', margin: 0 }}>
                            {gradeDescriptions[grade]}
                          </p>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                <div style={{ borderTop: '1px solid var(--color-gray-200)', paddingTop: 'var(--spacing-4)' }}>
                  <label style={{ display: 'block', marginBottom: 'var(--spacing-3)', fontWeight: 600, fontSize: 'var(--font-size-base)' }}>
                    Clinical Notes
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add any additional observations, recommendations, or clinical notes..."
                    style={{
                      width: '100%',
                      minHeight: '120px',
                      padding: 'var(--spacing-3)',
                      border: '1px solid var(--color-gray-300)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--font-size-sm)',
                      fontFamily: 'inherit',
                      resize: 'vertical'
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* ACTIONS */}
          <div style={{ display: 'flex', gap: 'var(--spacing-3)' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/doctor/queue')}
              style={{ flex: 1 }}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ flex: 1 }}
              disabled={submitting || doctorGrade === ''}
            >
              {submitting ? 'Submitting...' : 'Submit Review'}
            </button>
          </div>
        </form>
      </div>
    </AppShell>
  );
};
