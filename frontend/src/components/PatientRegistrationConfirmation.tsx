import React, { useState } from 'react';

interface ConfirmationData {
  patientCode: string;
  fullName: string;
  dateOfBirth: string;
}

interface PatientRegistrationConfirmationProps {
  data: ConfirmationData;
  onDismiss: () => void;
}

export const PatientRegistrationConfirmation: React.FC<PatientRegistrationConfirmationProps> = ({
  data,
  onDismiss,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(data.patientCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: 'var(--spacing-4)',
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: 'var(--radius-lg)',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        maxWidth: '600px',
        width: '100%',
        padding: 'var(--spacing-8)',
      }}>
        {/* Success Icon and Heading */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-6)' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '64px',
            height: '64px',
            backgroundColor: '#dcfce7',
            borderRadius: '50%',
            marginBottom: 'var(--spacing-4)',
          }}>
            <span style={{ fontSize: '32px' }}>✓</span>
          </div>
          <h2 style={{
            margin: '0 0 var(--spacing-2) 0',
            fontSize: 'var(--font-size-xl)',
            fontWeight: 600,
            color: 'var(--color-gray-900)',
          }}>
            Patient Registered Successfully
          </h2>
          <p style={{
            margin: '0',
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-gray-600)',
          }}>
            The patient has been added to the screening database
          </p>
        </div>

        {/* Patient Information Cards */}
        <div style={{
          display: 'grid',
          gap: 'var(--spacing-4)',
          marginBottom: 'var(--spacing-6)',
        }}>
          {/* Patient Name Card */}
          <div style={{
            padding: 'var(--spacing-4)',
            backgroundColor: 'var(--color-gray-50)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-gray-200)',
          }}>
            <p style={{
              margin: '0 0 var(--spacing-2) 0',
              fontSize: 'var(--font-size-xs)',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: 'var(--color-gray-500)',
            }}>
              Patient Name
            </p>
            <p style={{
              margin: '0',
              fontSize: 'var(--font-size-lg)',
              fontWeight: 600,
              color: 'var(--color-gray-900)',
            }}>
              {data.fullName}
            </p>
          </div>

          {/* Date of Birth Card */}
          <div style={{
            padding: 'var(--spacing-4)',
            backgroundColor: 'var(--color-gray-50)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-gray-200)',
          }}>
            <p style={{
              margin: '0 0 var(--spacing-2) 0',
              fontSize: 'var(--font-size-xs)',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: 'var(--color-gray-500)',
            }}>
              Date of Birth
            </p>
            <p style={{
              margin: '0',
              fontSize: 'var(--font-size-lg)',
              fontWeight: 600,
              color: 'var(--color-gray-900)',
            }}>
              {data.dateOfBirth}
            </p>
          </div>

          {/* Patient Code Card (Prominent) */}
          <div style={{
            padding: 'var(--spacing-5)',
            backgroundColor: '#eff6ff',
            borderRadius: 'var(--radius-md)',
            border: '2px solid #0284c7',
            textAlign: 'center',
          }}>
            <p style={{
              margin: '0 0 var(--spacing-3) 0',
              fontSize: 'var(--font-size-xs)',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: '#0369a1',
            }}>
              Patient Code
            </p>
            <p style={{
              margin: '0 0 var(--spacing-4) 0',
              fontSize: '32px',
              fontWeight: 700,
              fontFamily: 'monospace',
              color: '#0c4a6e',
              letterSpacing: '2px',
              wordBreak: 'break-all',
            }}>
              {data.patientCode}
            </p>
            <button
              onClick={handleCopyCode}
              style={{
                padding: 'var(--spacing-2) var(--spacing-4)',
                backgroundColor: '#0284c7',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-size-sm)',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onMouseOver={(e) => {
                (e.target as HTMLButtonElement).style.backgroundColor = '#0369a1';
              }}
              onMouseOut={(e) => {
                (e.target as HTMLButtonElement).style.backgroundColor = '#0284c7';
              }}
            >
              {copied ? 'Copied!' : 'Copy Patient Code'}
            </button>
          </div>
        </div>

        {/* Important Note */}
        <div style={{
          padding: 'var(--spacing-4)',
          backgroundColor: '#fef3c7',
          borderRadius: 'var(--radius-md)',
          border: '1px solid #fcd34d',
          marginBottom: 'var(--spacing-6)',
        }}>
          <p style={{
            margin: '0 0 var(--spacing-2) 0',
            fontSize: 'var(--font-size-sm)',
            fontWeight: 600,
            color: '#92400e',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-2)',
          }}>
            <span style={{ fontSize: '18px' }}>ℹ️</span>
            Important
          </p>
          <p style={{
            margin: '0',
            fontSize: 'var(--font-size-sm)',
            color: '#78350f',
            lineHeight: '1.5',
          }}>
            Please give this code to the patient — they will need it along with their date of birth to access their results.
          </p>
        </div>

        {/* Action Buttons */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 'var(--spacing-3)',
        }}>
          <button
            onClick={onDismiss}
            style={{
              padding: 'var(--spacing-3)',
              backgroundColor: 'var(--color-gray-100)',
              color: 'var(--color-gray-900)',
              border: '1px solid var(--color-gray-300)',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-sm)',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onMouseOver={(e) => {
              (e.target as HTMLButtonElement).style.backgroundColor = 'var(--color-gray-200)';
            }}
            onMouseOut={(e) => {
              (e.target as HTMLButtonElement).style.backgroundColor = 'var(--color-gray-100)';
            }}
          >
            Register Another Patient
          </button>
          <button
            onClick={() => {
              onDismiss();
            }}
            style={{
              padding: 'var(--spacing-3)',
              backgroundColor: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-sm)',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onMouseOver={(e) => {
              (e.target as HTMLButtonElement).style.backgroundColor = '#059669';
            }}
            onMouseOut={(e) => {
              (e.target as HTMLButtonElement).style.backgroundColor = '#10b981';
            }}
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
