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

  const normalizeUser = (rawUser?: User | null): User | null => {
    if (!rawUser) {
      return null;
    }

    const deducedRole = (() => {
      if (rawUser.role) {
        return rawUser.role;
      }

      if (typeof rawUser.is_admin !== 'undefined') {
        return rawUser.is_admin ? 'admin' : 'colaborador';
      }

      return 'colaborador';
    })();

    const deducedIsAdmin =
      typeof rawUser.is_admin !== 'undefined'
        ? rawUser.is_admin
        : deducedRole === 'admin';

    return {
      ...rawUser,
      role: deducedRole,
      is_admin: deducedIsAdmin,
    };
  };

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
        setUser(normalizeUser(response.user));
      } else {
        setUser(null);
      }
    } catch (error: unknown) {
      // 401 error is expected when user is not logged in
      if (
        typeof error === 'object' &&
        error !== null &&
        'response' in error &&
        (error as { response?: { status?: number } }).response?.status === 401
      ) {
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
      setUser(normalizeUser(response.user));
    } catch (error: unknown) {
      console.error('Login failed:', error);
      const detail =
        typeof error === 'object' && error !== null && 'response' in error
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      throw new Error(detail || (error instanceof Error ? error.message : 'Falha na autenticação'));
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
      setUser(normalizeUser(response.user));
    } catch (error: unknown) {
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
        setUser(normalizeUser(response.user));
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
