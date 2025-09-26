export type DocumentStatus =
  | 'pending'
  | 'available'
  | 'soft_deleted'
  | 'hard_deleted';

export interface PatientDocument {
  id: string;
  appointment_id: string;
  patient_id: string;
  original_file_name: string;
  sanitized_file_name: string;
  content_type: string;
  file_size: number;
  status: DocumentStatus;
  storage_key: string;
  uploader_user_id?: string | null;
  source_ip?: string | null;
  created_at: string;
  uploaded_at?: string | null;
  deleted_at?: string | null;
  deleted_by?: string | null;
  etag?: string | null;
}

export interface PatientDocumentList {
  documents: PatientDocument[];
}

export interface DownloadUrlPayload {
  url: string;
  expires_in: number;
}

export interface PresignUploadResponse {
  document_id: string;
  upload_url: string;
  headers: Record<string, string>;
  expires_in: number;
  storage_key: string;
}

export interface ConfirmUploadRequest {
  file_size: number;
  etag?: string | null;
}

export interface PresignUploadRequest {
  patient_id: string;
  file_name: string;
  content_type: string;
  file_size: number;
}

export interface ApiDataResponse<T> {
  success: boolean;
  message?: string;
  data: T;
  request_id?: string;
}
