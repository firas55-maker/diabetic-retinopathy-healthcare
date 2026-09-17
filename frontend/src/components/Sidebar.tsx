import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

interface SidebarProps {
  role: string;
  email: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ role, email }) => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getNavItems = () => {
    switch (role) {
      case 'doctor':
        return [
          { label: 'Dashboard', path: '/doctor/dashboard' },
          { label: 'Scan Queue', path: '/doctor/queue' },
          { label: 'My Patients', path: '/doctor/patients' },
          { label: 'Statistics', path: '/doctor/stats' },
        ];
      case 'technical_staff':
        return [
          { label: 'Dashboard', path: '/staff/dashboard' },
          { label: 'Register Patient', path: '/staff/register-patient' },
          { label: 'Upload Scan', path: '/staff/upload-scan' },
          { label: 'My Uploads', path: '/staff/my-uploads' },
        ];
      default:
        return [];
    }
  };

  const navItems = getNavItems();
  const roleLabel = role === 'doctor' ? 'Doctor' : role === 'technical_staff' ? 'Technical Staff' : 'Admin';

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Healthcare</h2>
        <p>{roleLabel}</p>
      </div>

      <nav>
        <ul className="nav-menu">
          {navItems.map((item) => (
            <li key={item.path} className="nav-item">
              <a
                href={item.path}
                className="nav-link"
                onClick={(e) => {
                  e.preventDefault();
                  navigate(item.path);
                }}
              >
                {item.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <div style={{ position: 'absolute', bottom: 0, width: '100%' }}>
        <div style={{ padding: '0 20px 20px 20px', fontSize: '12px', color: 'rgba(255,255,255,0.7)' }}>
          {email}
        </div>
        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  );
};
