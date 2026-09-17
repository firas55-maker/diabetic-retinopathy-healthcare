import React from 'react';
import { useAuth } from '../context/AuthContext';
import './Unauthorized.css';

export const Unauthorized: React.FC = () => {
  const { role } = useAuth();

  return (
    <div className="unauthorized-container">
      <div className="unauthorized-card">
        <h1>❌ Access Denied</h1>
        <p>
          You don't have permission to access this page.
          Your current role is: <strong>{role || 'Unknown'}</strong>
        </p>
        <a href="/">Go Home</a>
      </div>
    </div>
  );
};
