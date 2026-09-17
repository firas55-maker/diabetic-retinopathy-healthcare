import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, email, role } = useAuth();
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  React.useEffect(() => {
    console.log('[AppShell] Current role:', role);
  }, [role]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getDoctorNavItems = () => [
    { label: 'Dashboard', path: '/doctor/dashboard', icon: '📊' },
    { label: 'Scan Queue', path: '/doctor/queue', icon: '⏳' },
    { label: 'My Patients', path: '/doctor/patients', icon: '👥' },
  ];

  const getStaffNavItems = () => [
    { label: 'Dashboard', path: '/staff/dashboard', icon: '📊' },
    { label: 'Register Patient', path: '/staff/register-patient', icon: '➕' },
    { label: 'Upload Scan', path: '/staff/upload-scan', icon: '📤' },
    { label: 'Upload History', path: '/staff/uploads', icon: '📋' },
  ];

  // Role-based navigation: strictly enforce role-specific items
  const navItems = role === 'doctor'
    ? getDoctorNavItems()
    : role === 'technical_staff'
    ? getStaffNavItems()
    : [];

  const roleLabel = role === 'doctor' ? 'Doctor' : role === 'technical_staff' ? 'Technical Staff' : 'User';

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="app-container">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">👁️</div>
            <div className="sidebar-logo-text">
              <h2>RetinalCare</h2>
              <p>Screening Platform</p>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section">
            <div className="nav-section-title">Navigation</div>
            {navItems.map((item) => (
              <div key={item.path} className="nav-item">
                <a
                  href={item.path}
                  className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    navigate(item.path);
                  }}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </a>
              </div>
            ))}
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="user-info-small">
            <p><strong>{roleLabel}</strong></p>
            <p>{email}</p>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            Sign Out
          </button>
        </div>
      </aside>

      {/* MAIN CONTAINER */}
      <div className="main-container">
        {/* TOP BAR */}
        <header className="topbar">
          <h1 className="topbar-title">Healthcare Screening Platform</h1>
          <div className="topbar-actions">
            <button className="notification-bell" title="Notifications">
              🔔
              <span className="notification-badge"></span>
            </button>
          </div>
        </header>

        {/* MAIN CONTENT */}
        <main className="main-content">
          <div className="page-wrapper">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
