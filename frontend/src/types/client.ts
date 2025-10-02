import type { Appointment } from './appointment';
import type { PaginationInfo } from './appointment';

export interface ConvenioInfo {
  numero_convenio?: string | null;
  nome_convenio?: string | null;
  carteira_convenio?: string | null;
  primeira_utilizacao?: string | null;
  ultima_utilizacao?: string | null;
}

export interface Client {
  id: string;
  nome_completo: string;
  cpf: string;
  telefone?: string | null;
  email?: string | null;
  observacoes?: string | null;
  numero_convenio?: string | null;
  nome_convenio?: string | null;
  carteira_convenio?: string | null;
  convenios_historico: ConvenioInfo[];
  appointment_ids: string[];
  appointment_count: number;
  last_appointment_at?: string | null;
  last_address?: string | null;
  last_address_normalized?: Record<string, string | null> | null;
  created_at: string;
  updated_at?: string | null;
}

export type ClientSummary = Client;

export interface ClientListResponse {
  success: boolean;
  message?: string;
  clients: ClientSummary[];
  pagination: PaginationInfo;
}

export interface ClientDetailResponse {
  success: boolean;
  message?: string;
  client: Client;
  history: Appointment[];
}

export interface ClientResponse {
  success: boolean;
  message?: string;
  data: Client;
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

export interface ClientFilter {
  search?: string;
  cpf?: string;
  page?: number;
  page_size?: number;
}

export interface ClientFormData {
  nome_completo: string;
  cpf: string;
  telefone?: string;
  email?: string;
  observacoes?: string;
  numero_convenio?: string;
  nome_convenio?: string;
  carteira_convenio?: string;
}
