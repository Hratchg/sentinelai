/**
 * Authentication Context
 *
 * Manages user authentication state across the application.
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface User {
  user_id: string;
  username: string;
  email: string;
  full_name?: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const apiBaseUrl = 'http://localhost:8000';

  // Load token from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('sentinelai_token');
    const storedUser = localStorage.getItem('sentinelai_user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));

      // Set axios default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }

    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    try {
      // Create form data for OAuth2 password flow
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post(`${apiBaseUrl}/api/v1/auth/login`, formData);

      const { access_token, user: userData } = response.data;

      // Store token and user
      localStorage.setItem('sentinelai_token', access_token);
      localStorage.setItem('sentinelai_user', JSON.stringify(userData));

      setToken(access_token);
      setUser(userData);

      // Set axios default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    } catch (error: any) {
      console.error('Login failed:', error);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const register = async (username: string, email: string, password: string, fullName?: string) => {
    try {
      const response = await axios.post(`${apiBaseUrl}/api/v1/auth/register`, {
        username,
        email,
        password,
        full_name: fullName || null
      });

      const { access_token, user: userData } = response.data;

      // Store token and user
      localStorage.setItem('sentinelai_token', access_token);
      localStorage.setItem('sentinelai_user', JSON.stringify(userData));

      setToken(access_token);
      setUser(userData);

      // Set axios default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    } catch (error: any) {
      console.error('Registration failed:', error);
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  };

  const logout = () => {
    // Clear storage
    localStorage.removeItem('sentinelai_token');
    localStorage.removeItem('sentinelai_user');

    // Clear state
    setToken(null);
    setUser(null);

    // Remove axios auth header
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    isAuthenticated: !!token,
    isLoading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
