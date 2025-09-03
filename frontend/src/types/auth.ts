/**
 * Authentication-related TypeScript type definitions
 */

export interface User {
  id: string;
  email: string;
  name: string;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  name: string;
  password: string;
  is_admin?: boolean;
}

export interface UserUpdateData {
  name?: string;
  is_admin?: boolean;
  is_active?: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  user: User;
}

export interface AuthStatusResponse {
  success: boolean;
  message: string;
  user?: User;
}

export interface FirstAdminCheckResponse {
  needs_setup: boolean;
  message: string;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  refreshUser: () => Promise<void>;
}

export interface UserListResponse {
  users: User[];
  total: number;
  limit: number;
  offset: number;
  has_next: boolean;
}

export interface UserListParams {
  limit?: number;
  offset?: number;
}

export interface ApiError {
  detail: string;
  status?: number;
}