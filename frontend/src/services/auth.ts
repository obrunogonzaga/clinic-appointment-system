/**
 * Authentication API service
 */

import axios from 'axios';
import type {
  AuthResponse,
  AuthStatusResponse,
  FirstAdminCheckResponse,
  LoginCredentials,
  RegisterData,
} from '../types/auth';

const API_BASE_URL = window.ENV?.API_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const authApi = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/auth`,
  timeout: 10000,
  withCredentials: true, // Important for cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor to handle authentication errors
authApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Only redirect if not already on auth pages
      const currentPath = window.location.pathname;
      if (!currentPath.includes('/login') && !currentPath.includes('/setup')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  /**
   * Check if system needs initial admin setup
   */
  async checkFirstAdminSetup(): Promise<FirstAdminCheckResponse> {
    const response = await authApi.get<FirstAdminCheckResponse>('/setup-check');
    return response.data;
  },

  /**
   * Register first admin user
   */
  async registerFirstAdmin(userData: RegisterData): Promise<AuthResponse> {
    const response = await authApi.post<AuthResponse>('/register', {
      ...userData,
      is_admin: true,
    });
    return response.data;
  },

  /**
   * Login user with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await authApi.post<AuthResponse>('/login', credentials);
    return response.data;
  },

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    await authApi.post('/logout');
  },

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<AuthStatusResponse> {
    const response = await authApi.get<AuthStatusResponse>('/me');
    return response.data;
  },

  /**
   * Create new user (admin only)
   */
  async createUser(userData: RegisterData): Promise<AuthResponse> {
    const response = await authApi.post<AuthResponse>('/users', userData);
    return response.data;
  },

  /**
   * Check if user is authenticated by calling /me endpoint
   */
  async checkAuth(): Promise<boolean> {
    try {
      const response = await this.getCurrentUser();
      return response.success && !!response.user;
    } catch {
      return false;
    }
  },
};

export default authService;