import React from 'react';
import { useAuth } from '../context/AuthContext';

export const Unauthorized: React.FC = () => {
  const { role } = useAuth();

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '40px',
        textAlign: 'center',
        maxWidth: '400px',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
      }}>
        <h1 style={{ margin: '0 0 20px 0', color: '#e74c3c', fontSize: '36px' }}>
          ❌ Access Denied
        </h1>
        <p style={{ color: '#666', marginBottom: '20px', lineHeight: '1.6' }}>
          You don't have permission to access this page.
          Your current role is: <strong>{role || 'Unknown'}</strong>
        </p>
        <a href="/" style={{
          display: 'inline-block',
          padding: '10px 20px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '6px',
          fontWeight: '600'
        }}>
          Go Home
        </a>
      </div>
    </div>
  );
};
