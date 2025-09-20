/**
 * Authentication-related TypeScript type definitions
 */

export type UserRole = 'admin' | 'motorista' | 'coletor' | 'colaborador';

export type UserStatus = 'pendente' | 'aprovado' | 'rejeitado' | 'suspenso' | 'inativo';

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  /** legacy fields kept for compatibility */
  is_admin?: boolean;
  is_active?: boolean;
  /** enhanced auth fields */
  role?: UserRole;
  status?: UserStatus;
  email_verified?: boolean;
  phone?: string | null;
  department?: string | null;
  created_by?: string | null;
  approved_by?: string | null;
  approved_at?: string | null;
  rejected_by?: string | null;
  rejected_at?: string | null;
  rejection_reason?: string | null;
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

export interface PublicRegisterData {
  email: string;
  name: string;
  password: string;
  role: Exclude<UserRole, 'admin'>;
  phone?: string;
  cpf?: string;
  department?: string;
  drivers_license?: string;
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
  refresh_token?: string;
}

export interface AuthStatusResponse {
  success: boolean;
  message: string;
  user?: User;
}

export interface VerifyEmailResponse {
  success: boolean;
  message: string;
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
