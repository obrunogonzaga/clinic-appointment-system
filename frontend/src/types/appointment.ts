export interface AppointmentTag {
  id: string;
  name: string;
  color: string;
}

export interface Appointment {
  id: string;
  nome_marca: string;
  nome_unidade: string;
  nome_paciente: string;
  data_agendamento?: string | null;
  hora_agendamento?: string | null;
  tipo_consulta?: string;
  cip?: string;
  status: string;
  telefone?: string;
  carro?: string;
  observacoes?: string;
  driver_id?: string;
  collector_id?: string;
  car_id?: string;
   logistics_package_id?: string;
   logistics_package_name?: string;
  canal_confirmacao?: string;
  data_confirmacao?: string;
  hora_confirmacao?: string;
  // Campos opcionais que podem vir a existir no backend
  cep?: string;
  endereco_coleta?: string;
  endereco_completo?: string;
  endereco_normalizado?: {
    rua?: string | null;
    numero?: string | null;
    complemento?: string | null;
    bairro?: string | null;
    cidade?: string | null;
    estado?: string | null;
    cep?: string | null;
  } | null;
  // Campos de documento do paciente
  documento_completo?: string;
  documento_normalizado?: {
    cpf?: string | null;
    rg?: string | null;
    cpf_formatted?: string | null;
    rg_formatted?: string | null;
  } | null;
  cpf?: string;
  rg?: string;
  numero_convenio?: string;
  nome_convenio?: string;
  carteira_convenio?: string;
  created_at: string;
  updated_at?: string;
  cadastrado_por?: string;
  agendado_por?: string;
  tags?: AppointmentTag[];
}

export interface AppointmentViewModel extends Appointment {
  cpfMasked: string;
  healthPlanLabel: string;
}

export interface AppointmentCreateRequest {
  nome_marca: string;
  nome_unidade: string;
  nome_paciente: string;
  cpf: string;
  data_agendamento?: string;
  hora_agendamento?: string;
  tipo_consulta?: string;
  cip?: string;
  status?: string;
  telefone: string;
  carro?: string;
  observacoes?: string;
  driver_id?: string;
  collector_id?: string;
  car_id?: string;
  logistics_package_id?: string;
  numero_convenio?: string;
  nome_convenio?: string;
  carteira_convenio?: string;
  tags?: string[];
}

export interface AppointmentFilter {
  nome_unidade?: string;
  nome_marca?: string;
  data?: string;
  status?: string;
  driver_id?: string;
  page?: number;
  page_size?: number;
  scope?: 'current' | 'history' | 'unscheduled';
}

export interface PaginationInfo {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface AppointmentListResponse {
  success: boolean;
  message?: string;
  appointments: Appointment[];
  pagination: PaginationInfo;
}

export interface ExcelUploadResponse {
  success: boolean;
  message: string;
  filename?: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  imported_appointments: number;
  duplicates_found: number;
  errors: string[];
  processing_time?: number;
  past_appointments_blocked?: number;
  past_appointments_examples?: string[];
}

export interface FilterOptions {
  success: boolean;
  message?: string;
  units: string[];
  brands: string[];
  statuses: string[];
  max_tags_per_appointment?: number;
}

export interface DashboardStats {
  success: boolean;
  message?: string;
  stats: {
    total_appointments: number;
    confirmed_appointments: number;
    cancelled_appointments: number;
    total_units: number;
    total_brands: number;
  };
}

export interface AdminDashboardKpi {
  label: string;
  value: number;
  trend?: number;
}

export interface AdminDashboardTrendPoint {
  date: string;
  value: number;
}

export interface AdminDashboardTopUnit {
  name: string;
  value: number;
}

export interface AdminDashboardResourceUtilization {
  label: string;
  utilization: number;
}

export type AdminDashboardAlertType = 'info' | 'warning' | 'error';

export interface AdminDashboardAlert {
  id: string;
  message: string;
  type: AdminDashboardAlertType;
}

export interface AdminDashboardMetricsResponse {
  success: boolean;
  message?: string;
  kpis: AdminDashboardKpi[];
  trend: AdminDashboardTrendPoint[];
  top_units: AdminDashboardTopUnit[];
  resource_utilization: AdminDashboardResourceUtilization[];
  alerts: AdminDashboardAlert[];
  period: {
    start: string;
    end: string;
  };
}

export interface AppointmentCreateResponse {
  success: boolean;
  message: string;
  data: Appointment;
}

export interface AppointmentUpdateRequest {
  nome_marca?: string | null;
  nome_unidade?: string | null;
  nome_paciente?: string | null;
  data_agendamento?: string | null;
  hora_agendamento?: string | null;
  tipo_consulta?: string | null;
  cip?: string | null;
  status?: string | null;
  telefone?: string | null;
  carro?: string | null;
  observacoes?: string | null;
  driver_id?: string | null;
  collector_id?: string | null;
  car_id?: string | null;
  logistics_package_id?: string | null;
  numero_convenio?: string | null;
  nome_convenio?: string | null;
  carteira_convenio?: string | null;
  tags?: string[];
  canal_confirmacao?: string | null;
  data_confirmacao?: string | null;
  hora_confirmacao?: string | null;
  cep?: string | null;
  endereco_normalizado?: {
    rua?: string | null;
    numero?: string | null;
    complemento?: string | null;
    bairro?: string | null;
    cidade?: string | null;
    estado?: string | null;
    cep?: string | null;
  } | null;
  documento_normalizado?: {
    cpf?: string | null;
    rg?: string | null;
    cpf_formatted?: string | null;
    rg_formatted?: string | null;
  } | null;
  cpf?: string | null;
  rg?: string | null;
}
