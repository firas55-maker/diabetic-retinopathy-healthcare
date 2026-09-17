import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  token: string | null;
  role: string | null;
  email: string | null;
  userId: string | null;
  login: (token: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [role, setRole] = useState<string | null>(() => localStorage.getItem('role'));
  const [email, setEmail] = useState<string | null>(() => localStorage.getItem('email'));
  const [userId, setUserId] = useState<string | null>(() => localStorage.getItem('userId'));

  const login = (newToken: string) => {
    try {
      const parts = newToken.split('.');
      if (parts.length !== 3) throw new Error('Invalid token format');

      // Decode JWT payload (second part)
      const decoded = JSON.parse(atob(parts[1]));

      // Validate required fields
      if (!decoded.role || !decoded.email || !decoded.user_id) {
        throw new Error('Missing required JWT fields: role, email, or user_id');
      }

      // Ensure valid role
      const validRoles = ['doctor', 'technical_staff', 'admin', 'patient'];
      if (!validRoles.includes(decoded.role)) {
        console.warn(`[AuthContext] Invalid role in token: '${decoded.role}'. Valid roles: ${validRoles.join(', ')}`);
      }

      setToken(newToken);
      setRole(decoded.role);
      setEmail(decoded.email);
      setUserId(decoded.user_id);

      localStorage.setItem('token', newToken);
      localStorage.setItem('role', decoded.role);
      localStorage.setItem('email', decoded.email);
      localStorage.setItem('userId', decoded.user_id);

      console.log(`[AuthContext] Login successful - Role: ${decoded.role}, Email: ${decoded.email}`);
    } catch (error) {
      console.error('[AuthContext] Failed to parse token:', error);
      // Clear any partially-set values on error
      setToken(null);
      setRole(null);
      setEmail(null);
      setUserId(null);
    }
  };

  const logout = () => {
    console.log('[AuthContext] Logout - clearing role:', role);
    setToken(null);
    setRole(null);
    setEmail(null);
    setUserId(null);

    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('email');
    localStorage.removeItem('userId');
  };

  const value: AuthContextType = {
    token,
    role,
    email,
    userId,
    login,
    logout,
    isAuthenticated: !!token && !!role,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
