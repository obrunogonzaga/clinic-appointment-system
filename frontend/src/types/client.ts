export interface Client {
  id: string;
  nome: string;
  cpf: string;
  telefone?: string | null;
  email?: string | null;
  observacoes?: string | null;
  total_agendamentos: number;
  ultimo_agendamento_em?: string | null;
  ultimo_status?: string | null;
  ultima_unidade?: string | null;
  ultima_marca?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface ClientHistoryEntry {
  appointment_id: string;
  data_agendamento?: string | null;
  hora_agendamento?: string | null;
  status?: string | null;
  nome_unidade?: string | null;
  nome_marca?: string | null;
  created_at: string;
}

export interface ClientCreateRequest {
  nome: string;
  cpf: string;
  telefone?: string | null;
  email?: string | null;
  observacoes?: string | null;
}

export interface ClientUpdateRequest {
  nome?: string;
  telefone?: string | null;
  email?: string | null;
  observacoes?: string | null;
}

export interface ClientListParams {
  search?: string;
  page?: number;
  page_size?: number;
}

export interface ClientPaginationInfo {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ClientListResponse {
  success: boolean;
  message?: string;
  clients: Client[];
  pagination: ClientPaginationInfo;
}

export interface ClientDetail extends Client {
  historico_agendamentos: ClientHistoryEntry[];
}

export interface ClientDataResponse {
  success: boolean;
  message?: string;
  data: ClientDetail;
}

export interface ClientDetailResponse {
  success: boolean;
  message?: string;
  client: ClientDetail;
}
