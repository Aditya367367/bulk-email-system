import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    const token = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (token && refreshToken) {
      // Set user as authenticated immediately to prevent flicker
      setIsAuthenticated(true);
      try {
        await verifyToken();
      } catch (error) {
        console.error('Token verification failed:', error);
        // Try to refresh token first before logging out
        try {
          await refreshToken();
          await verifyToken();
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          logout();
        }
      }
    } else {
      setLoading(false);
    }
  };

  const verifyToken = async () => {
    try {
      const response = await authAPI.getProfile();
      setUser(response.data.user);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Token verification error:', error);
      // If token is invalid, logout
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);
      const { access, refresh, user: userData } = response.data;
      
      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);
      
      setUser(userData);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
    setIsAuthenticated(false);
  };

  const refreshToken = async () => {
    try {
      const refresh = localStorage.getItem('refreshToken');
      if (!refresh) {
        throw new Error('No refresh token');
      }
      
      const response = await authAPI.refreshToken(refresh);
      const { access } = response.data;
      
      localStorage.setItem('accessToken', access);
      return access;
    } catch (error) {
      logout();
      throw error;
    }
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
