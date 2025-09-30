import type { PaginationInfo } from './appointment';

export interface ClientHistoryEntry {
  appointment_id: string;
  nome_marca?: string | null;
  nome_unidade?: string | null;
  nome_paciente?: string | null;
  data_agendamento?: string | null;
  hora_agendamento?: string | null;
  status?: string | null;
  tipo_consulta?: string | null;
  observacoes?: string | null;
  created_at: string;
}

export interface ClientSummary {
  id: string;
  nome_completo: string;
  cpf: string;
  cpf_formatado?: string | null;
  telefone?: string | null;
  email?: string | null;
  total_agendamentos: number;
  ultima_data_agendamento?: string | null;
  ultima_unidade?: string | null;
  ultima_marca?: string | null;
  ultima_consulta_tipo?: string | null;
  ultima_consulta_status?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface ClientDetail extends ClientSummary {
  observacoes?: string | null;
  numero_convenio?: string | null;
  nome_convenio?: string | null;
  carteira_convenio?: string | null;
  appointment_history: ClientHistoryEntry[];
}

export interface ClientCreateRequest {
  nome_completo: string;
  cpf: string;
  telefone?: string;
  email?: string;
  observacoes?: string;
  numero_convenio?: string;
  nome_convenio?: string;
  carteira_convenio?: string;
}

export interface ClientUpdateRequest {
  nome_completo?: string;
  telefone?: string;
  email?: string;
  observacoes?: string;
  numero_convenio?: string;
  nome_convenio?: string;
  carteira_convenio?: string;
}

export interface ClientListResponse {
  success: boolean;
  message?: string;
  clients: ClientSummary[];
  pagination: PaginationInfo;
}

export interface ClientResponse {
  success: boolean;
  message?: string;
  client: ClientDetail;
}
