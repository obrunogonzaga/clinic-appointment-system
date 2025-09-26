export type PatientDocumentStatus =
  | 'pending'
  | 'uploaded'
  | 'failed'
  | 'deleted';

export interface PatientDocument {
  id: string;
  appointment_id: string;
  patient_id: string;
  tenant_id?: string | null;
  file_name: string;
  sanitized_file_name: string;
  storage_key: string;
  content_type: string;
  file_size: number;
  status: PatientDocumentStatus;
  uploader_user_id?: string | null;
  created_at: string;
  uploaded_at?: string | null;
  source_ip?: string | null;
  etag?: string | null;
  deleted_at?: string | null;
  deleted_by?: string | null;
  hard_deleted_at?: string | null;
}

export interface ApiDataResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface ApiListResponse<T> {
  success: boolean;
  message: string;
  data: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface PatientDocumentPresignPayload {
  file_name: string;
  content_type: string;
  file_size: number;
  patient_id: string;
}

export interface PatientDocumentPresignData {
  document_id: string;
  upload_url: string;
  headers: Record<string, string>;
  storage_key: string;
  expires_at: string;
}

export interface PatientDocumentDownloadUrlData {
  download_url: string;
  expires_at: string;
}
