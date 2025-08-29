export interface Car {
  id: string;
  nome: string;
  unidade: string;
  placa?: string;
  modelo?: string;
  cor?: string;
  status: string;
  observacoes?: string;
  created_at: string;
  updated_at?: string;
}

export interface CarCreateRequest {
  nome: string;
  unidade: string;
  placa?: string;
  modelo?: string;
  cor?: string;
  status?: string;
  observacoes?: string;
}

export interface CarUpdateRequest {
  nome?: string;
  unidade?: string;
  placa?: string;
  modelo?: string;
  cor?: string;
  status?: string;
  observacoes?: string;
}

export interface CarFilter {
  nome?: string;
  unidade?: string;
  placa?: string;
  modelo?: string;
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

export interface CarListResponse {
  success: boolean;
  message?: string;
  cars: Car[];
  pagination: PaginationInfo;
}

export interface CarResponse {
  success: boolean;
  message?: string;
  data: Car;
}

export interface CarDeleteResponse {
  success: boolean;
  message: string;
}

export interface CarStats {
  success: boolean;
  message?: string;
  stats: {
    total_cars: number;
    active_cars: number;
    inactive_cars: number;
    maintenance_cars: number;
    sold_cars: number;
  };
}

export interface CarFilterOptions {
  success: boolean;
  message?: string;
  statuses: string[];
  unidades: string[];
}

export interface ActiveCar {
  id: string;
  nome: string;
  unidade: string;
  placa?: string;
}

export interface ActiveCarListResponse {
  success: boolean;
  message?: string;
  cars: ActiveCar[];
}

export interface CarValidationError {
  success: false;
  message: string;
  field?: string;
  errors: string[];
}

export interface CarFromStringRequest {
  car_string: string;
}

export interface CarFromStringResponse {
  success: boolean;
  message?: string;
  car?: Car;
  created: boolean;
}

// Car status constants
export const CAR_STATUS = {
  ATIVO: 'Ativo',
  INATIVO: 'Inativo',
  MANUTENCAO: 'Manutenção',
  VENDIDO: 'Vendido'
} as const;

export type CarStatus = typeof CAR_STATUS[keyof typeof CAR_STATUS];

// Car form field types
export interface CarFormData {
  nome: string;
  unidade: string;
  placa: string;
  modelo: string;
  cor: string;
  status: CarStatus;
  observacoes: string;
}

// Car table column types
export interface CarTableColumn {
  key: keyof Car;
  label: string;
  sortable?: boolean;
  width?: string;
}