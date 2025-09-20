/**
 * Authentication API service
 */

import axios from 'axios';
import type {
  AdminDashboardStats,
  AuthResponse,
  AuthStatusResponse,
  FirstAdminCheckResponse,
  LoginCredentials,
  PendingUsersResponse,
  PublicRegisterData,
  RegisterData,
  User,
  UserApprovalPayload,
  UserListParams,
  UserListResponse,
  UserRejectionPayload,
  UserUpdateData,
  VerifyEmailResponse,
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

const adminApi = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/admin`,
  timeout: 10000,
  withCredentials: true,
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

adminApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
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
   * Public self-registration (awaits admin approval)
   */
  async publicRegister(data: PublicRegisterData): Promise<User> {
    const response = await authApi.post<User>('/public-register', data);
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
   * Verify email using token sent via email
   */
  async verifyEmail(token: string): Promise<VerifyEmailResponse> {
    const response = await authApi.get<VerifyEmailResponse>(`/verify-email/${token}`);
    return response.data;
  },

  /**
   * Resend email verification to a user
   */
  async resendVerification(email: string): Promise<VerifyEmailResponse> {
    const response = await authApi.post<VerifyEmailResponse>('/resend-verification', {
      email,
    });
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

  /**
   * List all users with pagination (admin only)
   */
  async listUsers(params: UserListParams = {}): Promise<UserListResponse> {
    const searchParams = new URLSearchParams();
    if (params.limit) searchParams.set('limit', params.limit.toString());
    if (params.offset) searchParams.set('offset', params.offset.toString());
    if (params.status) searchParams.set('status', params.status);
    if (params.role) searchParams.set('role', params.role);

    const queryString = searchParams.toString();
    const response = await authApi.get<UserListResponse>(
      queryString ? `/users?${queryString}` : '/users'
    );
    return response.data;
  },

  /**
   * Update user information (admin only)
  */
  async updateUser(userId: string, data: UserUpdateData): Promise<User> {
    const response = await authApi.patch<User>(`/users/${userId}`, data);
    return response.data;
  },

  /**
   * Delete user (soft delete - admin only)
   */
  async deleteUser(userId: string): Promise<{ success: boolean; message: string }> {
    const response = await authApi.delete<{ success: boolean; message: string }>(
      `/users/${userId}`
    );
    return response.data;
  },

  /**
   * Fetch admin dashboard statistics
   */
  async getAdminDashboardStats(): Promise<AdminDashboardStats> {
    const response = await adminApi.get<AdminDashboardStats>('/dashboard/stats');
    return response.data;
  },

  /**
   * Fetch pending users awaiting approval
   */
  async getPendingUsers(params: { limit?: number; offset?: number } = {}): Promise<PendingUsersResponse> {
    const searchParams = new URLSearchParams();
    if (params.limit) searchParams.set('limit', params.limit.toString());
    if (params.offset) searchParams.set('offset', params.offset.toString());
    const queryString = searchParams.toString();
    const response = await adminApi.get<PendingUsersResponse>(
      queryString ? `/users/pending?${queryString}` : '/users/pending'
    );
    return response.data;
  },

  /**
   * Approve a pending user
   */
  async approvePendingUser(userId: string, payload: UserApprovalPayload = {}): Promise<User> {
    const response = await adminApi.post<User>(`/users/${userId}/approve`, payload);
    return response.data;
  },

  /**
   * Reject a pending user with reason
   */
  async rejectPendingUser(userId: string, payload: UserRejectionPayload): Promise<User> {
    const response = await adminApi.post<User>(`/users/${userId}/reject`, payload);
    return response.data;
  },
};

export default authService;
