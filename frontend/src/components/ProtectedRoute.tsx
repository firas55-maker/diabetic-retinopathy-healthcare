import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string | string[];
}

/**
 * ProtectedRoute: Enforces both authentication and role-based access control
 *
 * - Redirects unauthenticated users to /login
 * - Redirects authenticated users without required role to /unauthorized
 * - Logs all access attempts for debugging role-based access issues
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
}) => {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  // Check authentication
  if (!isAuthenticated) {
    console.warn(`[ProtectedRoute] Unauthenticated access attempt to ${location.pathname}`);
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role if required
  if (requiredRole) {
    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];

    // Log role verification attempt
    console.log(
      `[ProtectedRoute] Role verification: path=${location.pathname}, userRole=${role}, required=${roles.join(', ')}, authorized=${role && roles.includes(role)}`
    );

    if (!role || !roles.includes(role)) {
      console.error(
        `[ProtectedRoute] UNAUTHORIZED ACCESS: User with role '${role}' attempted to access ${location.pathname} (required: ${roles.join(', ')})`
      );
      return <Navigate to="/unauthorized" replace />;
    }
  }

  console.debug(`[ProtectedRoute] Access granted to ${location.pathname} for role: ${role}`);
  return <>{children}</>;
};

export const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, role } = useAuth();

  if (isAuthenticated && role) {
    // Redirect to appropriate dashboard based on role
    if (role === 'doctor') return <Navigate to="/doctor/dashboard" replace />;
    if (role === 'technical_staff') return <Navigate to="/staff/dashboard" replace />;
    if (role === 'admin') return <Navigate to="/admin/dashboard" replace />;
  }

  return <>{children}</>;
};
