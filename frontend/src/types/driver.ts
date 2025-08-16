export interface Driver {
  id: string;
  nome_completo: string;
  cnh: string;
  telefone: string;
  email?: string;
  data_nascimento?: string;
  endereco?: string;
  status: string;
  carro?: string;
  observacoes?: string;
  created_at: string;
  updated_at?: string;
}

export interface DriverCreateRequest {
  nome_completo: string;
  cnh: string;
  telefone: string;
  email?: string;
  data_nascimento?: string;
  endereco?: string;
  status?: string;
  carro?: string;
  observacoes?: string;
}

export interface DriverUpdateRequest {
  nome_completo?: string;
  cnh?: string;
  telefone?: string;
  email?: string;
  data_nascimento?: string;
  endereco?: string;
  status?: string;
  carro?: string;
  observacoes?: string;
}

export interface DriverFilter {
  nome_completo?: string;
  cnh?: string;
  telefone?: string;
  email?: string;
  status?: string;
  page?: number;
  page_size?: number;
}

export interface PaginationInfo {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface DriverListResponse {
  success: boolean;
  message?: string;
  drivers: Driver[];
  pagination: PaginationInfo;
}

export interface DriverResponse {
  success: boolean;
  message?: string;
  data: Driver;
}

export interface DriverDeleteResponse {
  success: boolean;
  message: string;
}

export interface DriverStats {
  success: boolean;
  message?: string;
  stats: {
    total_drivers: number;
    active_drivers: number;
    inactive_drivers: number;
    suspended_drivers: number;
  };
}

export interface DriverFilterOptions {
  success: boolean;
  message?: string;
  statuses: string[];
}

export interface ActiveDriver {
  id: string;
  nome_completo: string;
  cnh: string;
  telefone: string;
}

export interface ActiveDriverListResponse {
  success: boolean;
  message?: string;
  drivers: ActiveDriver[];
}

export interface DriverValidationError {
  success: false;
  message: string;
  field?: string;
  errors: string[];
}

// Driver status constants
export const DRIVER_STATUS = {
  ATIVO: 'Ativo',
  INATIVO: 'Inativo',
  SUSPENSO: 'Suspenso',
  FERIAS: 'Férias'
} as const;

export type DriverStatus = typeof DRIVER_STATUS[keyof typeof DRIVER_STATUS];

// Driver form field types
export interface DriverFormData {
  nome_completo: string;
  cnh: string;
  telefone: string;
  email: string;
  data_nascimento: string;
  endereco: string;
  status: DriverStatus;
  carro: string;
  observacoes: string;
}

// Driver table column types
export interface DriverTableColumn {
  key: keyof Driver;
  label: string;
  sortable?: boolean;
  width?: string;
}