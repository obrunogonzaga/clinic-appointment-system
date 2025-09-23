export interface Appointment {
  id: string;
  nome_marca: string;
  nome_unidade: string;
  nome_paciente: string;
  data_agendamento: string;
  hora_agendamento: string;
  tipo_consulta?: string;
  status: string;
  telefone?: string;
  carro?: string;
  observacoes?: string;
  driver_id?: string;
  collector_id?: string;
  car_id?: string;
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
  created_at: string;
  updated_at?: string;
}

export interface AppointmentViewModel extends Appointment {
  cpfMasked: string;
  healthPlanLabel: string;
}

export interface AppointmentCreateRequest {
  nome_marca: string;
  nome_unidade: string;
  nome_paciente: string;
  data_agendamento: string;
  hora_agendamento: string;
  tipo_consulta?: string;
  status?: string;
  telefone: string;
  carro?: string;
  observacoes?: string;
  driver_id?: string;
  collector_id?: string;
  numero_convenio?: string;
  nome_convenio?: string;
  carteira_convenio?: string;
}

export interface AppointmentFilter {
  nome_unidade?: string;
  nome_marca?: string;
  data?: string;
  status?: string;
  driver_id?: string;
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
}

export interface FilterOptions {
  success: boolean;
  message?: string;
  units: string[];
  brands: string[];
  statuses: string[];
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

export interface AppointmentCreateResponse {
  success: boolean;
  message: string;
  data: Appointment;
}
