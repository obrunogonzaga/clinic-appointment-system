/**
 * Authentication context for managing user state and auth operations
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../services/auth';
import type {
  AuthContextType,
  LoginCredentials,
  RegisterData,
  User,
} from '../types/auth';

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize authentication state on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setIsLoading(true);
      
      // Try to get current user directly (faster initialization)
      const response = await authService.getCurrentUser();
      
      if (response.success && response.user) {
        setUser(response.user);
      } else {
        setUser(null);
      }
    } catch (error: any) {
      // 401 error is expected when user is not logged in
      if (error.response?.status === 401) {
        setUser(null);
      } else {
        console.error('Failed to initialize auth:', error);
        setUser(null);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      setIsLoading(true);
      const response = await authService.login(credentials);
      setUser(response.user);
    } catch (error: any) {
      console.error('Login failed:', error);
      throw new Error(
        error.response?.data?.detail || 'Falha na autenticação'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      setIsLoading(true);
      await authService.logout();
    } catch (error) {
      console.error('Logout failed:', error);
      // Continue with logout even if API call fails
    } finally {
      setUser(null);
      setIsLoading(false);
      // Redirect to login page
      window.location.href = '/login';
    }
  };

  const register = async (data: RegisterData): Promise<void> => {
    try {
      setIsLoading(true);
      const response = await authService.registerFirstAdmin(data);
      setUser(response.user);
    } catch (error: any) {
      console.error('Registration failed:', error);
      // Preserve the original error to maintain response data
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const refreshUser = async (): Promise<void> => {
    try {
      const response = await authService.getCurrentUser();
      
      if (response.success && response.user) {
        setUser(response.user);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
      setUser(null);
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    register,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

export { AuthContext };