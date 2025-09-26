import { api } from './api';
import type {
  ApiDataResponse,
  ApiListResponse,
  PatientDocument,
  PatientDocumentDownloadUrlData,
  PatientDocumentPresignData,
  PatientDocumentPresignPayload,
} from '../types/patient-document';

function createConfig(tenantId?: string) {
  return {
    withCredentials: true as const,
    headers: tenantId ? { 'X-Tenant-ID': tenantId } : undefined,
  };
}

export const patientDocumentsAPI = {
  async list(
    appointmentId: string,
    tenantId?: string
  ): Promise<ApiListResponse<PatientDocument>> {
    const response = await api.get<ApiListResponse<PatientDocument>>(
      `/appointments/${appointmentId}/documents`,
      createConfig(tenantId)
    );
    return response.data;
  },

  async createPresignedUpload(
    appointmentId: string,
    payload: PatientDocumentPresignPayload,
    tenantId?: string
  ): Promise<PatientDocumentPresignData> {
    const response = await api.post<
      ApiDataResponse<PatientDocumentPresignData>
    >(
      `/appointments/${appointmentId}/documents/presign-upload`,
      payload,
      createConfig(tenantId)
    );
    return response.data.data;
  },

  async confirmUpload(
    appointmentId: string,
    documentId: string,
    payload: { etag?: string },
    tenantId?: string
  ): Promise<PatientDocument> {
    const response = await api.post<ApiDataResponse<PatientDocument>>(
      `/appointments/${appointmentId}/documents/${documentId}/confirm`,
      payload,
      createConfig(tenantId)
    );
    return response.data.data;
  },

  async getDownloadUrl(
    appointmentId: string,
    documentId: string,
    tenantId?: string
  ): Promise<PatientDocumentDownloadUrlData> {
    const response = await api.get<
      ApiDataResponse<PatientDocumentDownloadUrlData>
    >(
      `/appointments/${appointmentId}/documents/${documentId}/download-url`,
      createConfig(tenantId)
    );
    return response.data.data;
  },

  async deleteDocument(
    appointmentId: string,
    documentId: string,
    options: { hard?: boolean } = {},
    tenantId?: string
  ): Promise<PatientDocument> {
    const response = await api.delete<ApiDataResponse<PatientDocument>>(
      `/appointments/${appointmentId}/documents/${documentId}`,
      {
        ...createConfig(tenantId),
        params: { hard: options.hard ?? false },
      }
    );
    return response.data.data;
  },
};
