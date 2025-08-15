export interface Collector {
  id: string;
  nome_completo: string;
  cpf: string;
  telefone: string;
  email?: string;
  data_nascimento?: string;
  endereco?: string;
  status: string;
  observacoes?: string;
  registro_profissional?: string;
  especializacao?: string;
  created_at: string;
  updated_at?: string;
}

export interface CollectorCreateRequest {
  nome_completo: string;
  cpf: string;
  telefone: string;
  email?: string;
  data_nascimento?: string;
  endereco?: string;
  status?: string;
  observacoes?: string;
  registro_profissional?: string;
  especializacao?: string;
}

export interface CollectorUpdateRequest {
  nome_completo?: string;
  cpf?: string;
  telefone?: string;
  email?: string;
  data_nascimento?: string;
  endereco?: string;
  status?: string;
  observacoes?: string;
  registro_profissional?: string;
  especializacao?: string;
}

export interface CollectorFilter {
  nome_completo?: string;
  cpf?: string;
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

export interface CollectorListResponse {
  success: boolean;
  message?: string;
  collectors: Collector[];
  pagination: PaginationInfo;
}

export interface CollectorResponse {
  success: boolean;
  message?: string;
  data: Collector;
}

export interface CollectorDeleteResponse {
  success: boolean;
  message: string;
}

export interface CollectorStats {
  success: boolean;
  message?: string;
  stats: {
    total_collectors: number;
    active_collectors: number;
    inactive_collectors: number;
    suspended_collectors: number;
  };
}

export interface CollectorFilterOptions {
  success: boolean;
  message?: string;
  statuses: string[];
}

export interface ActiveCollector {
  id: string;
  nome_completo: string;
  cpf: string;
  telefone: string;
}

export interface ActiveCollectorListResponse {
  success: boolean;
  message?: string;
  collectors: ActiveCollector[];
}

export interface CollectorValidationError {
  success: false;
  message: string;
  field?: string;
  errors: string[];
}

// Collector status constants
export const COLLECTOR_STATUS = {
  ATIVO: 'Ativo',
  INATIVO: 'Inativo',
  SUSPENSO: 'Suspenso',
  FERIAS: 'Férias'
} as const;

export type CollectorStatus = typeof COLLECTOR_STATUS[keyof typeof COLLECTOR_STATUS];

// Collector form field types
export interface CollectorFormData {
  nome_completo: string;
  cpf: string;
  telefone: string;
  email: string;
  data_nascimento: string;
  endereco: string;
  status: CollectorStatus;
  observacoes: string;
  registro_profissional: string;
  especializacao: string;
}

// Collector table column types
export interface CollectorTableColumn {
  key: keyof Collector;
  label: string;
  sortable?: boolean;
  width?: string;
}
