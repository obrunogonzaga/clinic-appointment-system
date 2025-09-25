export interface LogisticsPackage {
  id: string;
  nome: string;
  descricao?: string | null;
  driver_id: string;
  driver_nome: string;
  collector_id: string;
  collector_nome: string;
  car_id: string;
  car_nome: string;
  car_unidade?: string | null;
  car_display_name: string;
  status: 'Ativo' | 'Inativo';
}

export interface LogisticsPackageCreateRequest {
  nome: string;
  descricao?: string;
  driver_id: string;
  collector_id: string;
  car_id: string;
}

export interface LogisticsPackageUpdateRequest {
  nome?: string;
  descricao?: string | null;
  driver_id?: string;
  collector_id?: string;
  car_id?: string;
  status?: 'Ativo' | 'Inativo';
}

export interface LogisticsPackageListResponse {
  success: boolean;
  message?: string;
  data: LogisticsPackage[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface LogisticsPackageResponse {
  success: boolean;
  message?: string;
  data: LogisticsPackage;
}

export interface LogisticsPackageDeleteResponse {
  success: boolean;
  message: string;
}
