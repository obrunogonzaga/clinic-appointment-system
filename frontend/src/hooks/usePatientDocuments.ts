import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { patientDocumentsAPI } from '../services/patientDocuments';
import type {
  ApiListResponse,
  PatientDocument,
} from '../types/patient-document';

export const patientDocumentsQueryKeys = {
  all: ['patient-documents'] as const,
  list: (appointmentId: string, tenantId?: string) =>
    [
      ...patientDocumentsQueryKeys.all,
      'list',
      appointmentId,
      tenantId ?? 'default',
    ] as const,
};

export function usePatientDocuments(
  appointmentId: string | null,
  tenantId?: string
) {
  return useQuery<ApiListResponse<PatientDocument>, Error>({
    queryKey: appointmentId
      ? patientDocumentsQueryKeys.list(appointmentId, tenantId)
      : [...patientDocumentsQueryKeys.all, 'list', 'unknown'],
    queryFn: () => {
      if (!appointmentId) {
        throw new Error('Agendamento não informado');
      }
      return patientDocumentsAPI.list(appointmentId, tenantId);
    },
    enabled: Boolean(appointmentId),
  });
}

interface UploadArgs {
  appointmentId: string;
  patientId: string;
  file: File;
  tenantId?: string;
}

export function usePatientDocumentUpload() {
  const queryClient = useQueryClient();

  return useMutation<PatientDocument, Error, UploadArgs>({
    mutationFn: async ({ appointmentId, patientId, file, tenantId }) => {
      const presign = await patientDocumentsAPI.createPresignedUpload(
        appointmentId,
        {
          file_name: file.name,
          content_type:
            file.type && file.type.length > 0
              ? file.type
              : 'application/octet-stream',
          file_size: file.size,
          patient_id: patientId,
        },
        tenantId
      );

      const uploadHeaders: Record<string, string> = { ...presign.headers };
      if (!uploadHeaders['Content-Type']) {
        uploadHeaders['Content-Type'] =
          file.type && file.type.length > 0
            ? file.type
            : 'application/octet-stream';
      }

      const uploadResponse = await fetch(presign.upload_url, {
        method: 'PUT',
        body: file,
        headers: uploadHeaders,
      });

      if (!uploadResponse.ok) {
        const errorBody = await uploadResponse.text().catch(() => '');
        throw new Error(
          errorBody || 'Falha ao enviar arquivo para o storage de documentos.'
        );
      }

      const etagHeader = uploadResponse.headers.get('ETag');
      const etag = etagHeader ? etagHeader.replace(/"/g, '') : undefined;

      return patientDocumentsAPI.confirmUpload(
        appointmentId,
        presign.document_id,
        { etag },
        tenantId
      );
    },
    onSuccess: async (_, variables) => {
      await queryClient.invalidateQueries({
        queryKey: patientDocumentsQueryKeys.list(
          variables.appointmentId,
          variables.tenantId
        ),
      });
    },
  });
}

interface DeleteArgs {
  appointmentId: string;
  documentId: string;
  hard?: boolean;
  tenantId?: string;
}

export function useDeletePatientDocument() {
  const queryClient = useQueryClient();

  return useMutation<PatientDocument, Error, DeleteArgs>({
    mutationFn: ({ appointmentId, documentId, hard, tenantId }) =>
      patientDocumentsAPI.deleteDocument(
        appointmentId,
        documentId,
        { hard },
        tenantId
      ),
    onSuccess: async (_, variables) => {
      await queryClient.invalidateQueries({
        queryKey: patientDocumentsQueryKeys.list(
          variables.appointmentId,
          variables.tenantId
        ),
      });
    },
  });
}
