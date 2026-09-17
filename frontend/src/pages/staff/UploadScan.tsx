import React, { useState } from 'react';
import { AppShell } from '../../components/AppShell';
import api from '../../services/api';

export const UploadScan: React.FC = () => {
  const [step, setStep] = useState<'patient' | 'upload' | 'confirm'>('patient');
  const [patientCode, setPatientCode] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [uploadedScanId, setUploadedScanId] = useState('');

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
        setError('');
      } else {
        setError('Please upload a valid image file (JPG, PNG, etc.)');
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files[0]) {
      const file = files[0];
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
        setError('');
      } else {
        setError('Please upload a valid image file (JPG, PNG, etc.)');
      }
    }
  };

  const handlePatientSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!patientCode.trim()) {
      setError('Please enter a patient code');
      return;
    }
    setError('');
    setStep('upload');
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select an image file');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const response = await api.uploadScan(patientCode, selectedFile);
      setUploadedScanId(response.id || '');
      setStep('confirm');
    } catch (err: any) {
      console.error('Failed to upload scan:', err);
      setError(err.response?.data?.detail || 'Failed to upload scan. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-header-title">Upload Retinal Scan</h1>
        <p className="page-header-desc">Add a new screening image for a patient</p>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-6)' }}>{error}</div>}

      {/* STEP INDICATOR */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: 'var(--spacing-4)',
        marginBottom: 'var(--spacing-8)',
        alignItems: 'center'
      }}>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          opacity: step === 'patient' || step === 'upload' || step === 'confirm' ? 1 : 0.5
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            backgroundColor: step === 'patient' ? 'var(--color-primary)' : 'var(--color-success)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            marginBottom: 'var(--spacing-2)'
          }}>
            {step === 'patient' ? '1' : '✓'}
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', margin: 0 }}>Patient</p>
        </div>

        <div style={{ flex: 1, height: '2px', backgroundColor: step === 'upload' || step === 'confirm' ? 'var(--color-success)' : 'var(--color-gray-300)' }} />

        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          opacity: step === 'upload' || step === 'confirm' ? 1 : 0.5
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            backgroundColor: step === 'upload' ? 'var(--color-primary)' : step === 'confirm' ? 'var(--color-success)' : 'var(--color-gray-300)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            marginBottom: 'var(--spacing-2)'
          }}>
            {step === 'confirm' ? '✓' : '2'}
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', margin: 0 }}>Image</p>
        </div>

        <div style={{ flex: 1, height: '2px', backgroundColor: step === 'confirm' ? 'var(--color-success)' : 'var(--color-gray-300)' }} />

        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          opacity: step === 'confirm' ? 1 : 0.5
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            backgroundColor: step === 'confirm' ? 'var(--color-primary)' : 'var(--color-gray-300)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            marginBottom: 'var(--spacing-2)'
          }}>
            3
          </div>
          <p style={{ fontSize: 'var(--font-size-sm)', margin: 0 }}>Confirm</p>
        </div>
      </div>

      {/* STEP 1: PATIENT SELECTION */}
      {step === 'patient' && (
        <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
          <div className="card-header">
            <h3>Select Patient</h3>
          </div>
          <form onSubmit={handlePatientSubmit} className="card-body">
            <div style={{ display: 'grid', gap: 'var(--spacing-6)' }}>
              <div>
                <label style={{ display: 'block', marginBottom: 'var(--spacing-3)', fontWeight: 600, fontSize: 'var(--font-size-base)' }}>
                  Patient Code
                </label>
                <input
                  type="text"
                  value={patientCode}
                  onChange={(e) => setPatientCode(e.target.value)}
                  placeholder="Enter the patient code (e.g., PT-001-ABC)"
                  style={{ padding: 'var(--spacing-3)', fontSize: 'var(--font-size-base)' }}
                  required
                  autoFocus
                />
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', marginTop: 'var(--spacing-2)' }}>
                  Find this code on the patient's registration card or in the patient database
                </p>
              </div>

              <button type="submit" className="btn btn-primary btn-block" style={{ height: '48px' }}>
                Continue to Image Upload
              </button>
            </div>
          </form>
        </div>
      )}

      {/* STEP 2: IMAGE UPLOAD */}
      {step === 'upload' && (
        <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
          <div className="card-header">
            <h3>Upload Retinal Image</h3>
          </div>
          <form onSubmit={handleUploadSubmit} className="card-body">
            <div style={{ display: 'grid', gap: 'var(--spacing-6)' }}>
              {/* PATIENT INFO */}
              <div style={{ padding: 'var(--spacing-4)', backgroundColor: 'var(--color-gray-50)', borderRadius: 'var(--radius-md)' }}>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-600)', margin: 0, marginBottom: 'var(--spacing-1)' }}>
                  Patient Code
                </p>
                <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 'bold', margin: 0, color: 'var(--color-primary)' }}>
                  {patientCode}
                </p>
              </div>

              {/* DRAG & DROP AREA */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                style={{
                  border: `2px dashed ${dragActive ? 'var(--color-primary)' : 'var(--color-gray-300)'}`,
                  borderRadius: 'var(--radius-lg)',
                  padding: 'var(--spacing-8)',
                  textAlign: 'center',
                  backgroundColor: dragActive ? 'rgba(30, 123, 203, 0.05)' : 'var(--color-gray-50)',
                  transition: 'all 0.2s',
                  cursor: 'pointer'
                }}
              >
                <p style={{ fontSize: 'var(--font-size-2xl)', margin: '0 0 var(--spacing-3) 0' }}>📸</p>
                <p style={{ margin: 0, fontWeight: 600, marginBottom: 'var(--spacing-1)' }}>
                  {selectedFile ? selectedFile.name : 'Drag and drop your image here'}
                </p>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', margin: 0 }}>
                  or click to select a file
                </p>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                  id="file-input"
                />
                <label htmlFor="file-input" style={{ cursor: 'pointer' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ marginTop: 'var(--spacing-4)' }}
                    onClick={() => document.getElementById('file-input')?.click()}
                  >
                    Select File
                  </button>
                </label>
              </div>

              {selectedFile && (
                <div style={{ padding: 'var(--spacing-4)', backgroundColor: 'var(--color-success-light)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-success)' }}>
                  <p style={{ fontSize: 'var(--font-size-sm)', margin: 0, color: 'var(--color-success-dark)' }}>
                    ✓ File selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                </div>
              )}

              <div style={{ display: 'flex', gap: 'var(--spacing-3)' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setStep('patient');
                    setSelectedFile(null);
                  }}
                  style={{ flex: 1 }}
                >
                  Back
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={!selectedFile || loading}
                  style={{ flex: 1 }}
                >
                  {loading ? 'Uploading...' : 'Upload Image'}
                </button>
              </div>
            </div>
          </form>
        </div>
      )}

      {/* STEP 3: CONFIRMATION */}
      {step === 'confirm' && (
        <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
          <div className="card-header">
            <h3>Upload Successful</h3>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gap: 'var(--spacing-6)', textAlign: 'center' }}>
              <div style={{ fontSize: 'var(--font-size-4xl)' }}>✅</div>

              <div>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', margin: '0 0 var(--spacing-1) 0', textTransform: 'uppercase', fontWeight: 600 }}>
                  Scan ID
                </p>
                <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 'bold', margin: 0, color: 'var(--color-primary)', wordBreak: 'break-all' }}>
                  {uploadedScanId}
                </p>
              </div>

              <div style={{ padding: 'var(--spacing-4)', backgroundColor: 'var(--color-gray-50)', borderRadius: 'var(--radius-md)', textAlign: 'left' }}>
                <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-gray-600)', margin: '0 0 var(--spacing-2) 0', textTransform: 'uppercase', fontWeight: 600 }}>
                  What happens next?
                </p>
                <ol style={{ margin: 0, paddingLeft: 'var(--spacing-4)', color: 'var(--color-gray-700)', fontSize: 'var(--font-size-sm)' }}>
                  <li style={{ marginBottom: 'var(--spacing-2)' }}>The image will be processed by our AI system</li>
                  <li style={{ marginBottom: 'var(--spacing-2)' }}>Initial analysis will be available within minutes</li>
                  <li>A doctor will review and finalize the diagnosis</li>
                </ol>
              </div>

              <div style={{ display: 'flex', gap: 'var(--spacing-3)' }}>
                <button
                  className="btn btn-secondary btn-block"
                  onClick={() => {
                    setStep('patient');
                    setPatientCode('');
                    setSelectedFile(null);
                    setSuccess(false);
                    setError('');
                  }}
                >
                  Upload Another Scan
                </button>
                <button
                  className="btn btn-primary btn-block"
                  onClick={() => window.location.href = '/staff/uploads'}
                >
                  View Upload History
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
};
