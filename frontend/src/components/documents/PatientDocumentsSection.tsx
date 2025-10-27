import { useMemo, useRef, useState } from 'react';
import {
  useDeletePatientDocument,
  usePatientDocumentUpload,
  usePatientDocuments,
} from '../../hooks/usePatientDocuments';
import type { PatientDocument } from '../../types/patient-document';
import { formatDate } from '../../utils/dateUtils';
import { patientDocumentsAPI } from '../../services/patientDocuments';

const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/heic',
];

const ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'webp', 'heic'];
const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;

interface PatientDocumentsSectionProps {
  appointmentId: string;
  patientId: string;
  tenantId?: string;
  canManage: boolean;
}

interface DocumentActionState {
  deletingId: string | null;
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const exponent = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1
  );
  const value = bytes / 1024 ** exponent;
  return `${value.toFixed(value >= 10 || exponent === 0 ? 0 : 1)} ${units[exponent]}`;
};

const resolveStatusBadge = (status: PatientDocument['status']) => {
  switch (status) {
    case 'uploaded':
      return 'bg-green-100 text-green-800';
    case 'deleted':
      return 'bg-red-100 text-red-800';
    case 'failed':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const normalizeExtension = (fileName: string): string | undefined => {
  const parts = fileName.split('.');
  if (parts.length < 2) {
    return undefined;
  }
  return parts.pop()?.toLowerCase();
};

export function PatientDocumentsSection({
  appointmentId,
  patientId,
  tenantId,
  canManage,
}: PatientDocumentsSectionProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [{ deletingId }, setActionState] = useState<DocumentActionState>({
    deletingId: null,
  });

  const {
    data: listResponse,
    isLoading,
    isError,
    error,
  } = usePatientDocuments(appointmentId, tenantId);
  const uploadMutation = usePatientDocumentUpload();
  const deleteMutation = useDeletePatientDocument();

  const documents = useMemo(
    () => listResponse?.data ?? [],
    [listResponse]
  );

  const allowedTypesDescription = 'PDF, JPG, JPEG, PNG, WEBP ou HEIC';

  const handleOpenFileDialog = () => {
    inputRef.current?.click();
  };

  const validateFile = (file: File): string | null => {
    const mimeAllowed = ALLOWED_MIME_TYPES.includes(file.type);
    const extension = normalizeExtension(file.name);
    const extensionAllowed = extension
      ? ALLOWED_EXTENSIONS.includes(extension)
      : false;
    if (!mimeAllowed && !extensionAllowed) {
      return `Formato não suportado: ${file.name}. Tipos permitidos: ${allowedTypesDescription}.`;
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      return `${file.name} excede o limite de 10 MB.`;
    }
    return null;
  };

  const uploadFile = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      throw new Error(validationError);
    }

    await uploadMutation.mutateAsync({
      appointmentId,
      patientId,
      file,
      tenantId,
    });
  };

  const handleFiles = async (files: FileList | File[]) => {
    if (!canManage) {
      return;
    }
    setFeedbackMessage(null);
    setErrorMessage(null);

    const queue = Array.from(files);
    if (queue.length === 0) {
      return;
    }

    try {
      for (const file of queue) {
        await uploadFile(file);
      }
      setFeedbackMessage(
        queue.length === 1
          ? 'Documento enviado com sucesso.'
          : `${queue.length} documentos enviados com sucesso.`
      );
    } catch (uploadError) {
      const message =
        uploadError instanceof Error
          ? uploadError.message
          : 'Falha ao enviar documento.';
      setErrorMessage(message);
    }
  };

  const onInputChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (!event.target.files) {
      return;
    }
    await handleFiles(event.target.files);
    event.target.value = '';
  };

  const onDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    if (!canManage) {
      return;
    }
    event.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    if (!canManage) {
      return;
    }
    event.preventDefault();
    setIsDragging(false);
  };

  const onDrop = async (event: React.DragEvent<HTMLDivElement>) => {
    if (!canManage) {
      return;
    }
    event.preventDefault();
    setIsDragging(false);
    await handleFiles(event.dataTransfer.files);
  };

  const handleDownload = async (document: PatientDocument) => {
    try {
      const response = await patientDocumentsAPI.getDownloadUrl(
        appointmentId,
        document.id,
        tenantId
      );
      window.open(response.download_url, '_blank', 'noopener');
    } catch (downloadError) {
      const message =
        downloadError instanceof Error
          ? downloadError.message
          : 'Não foi possível gerar o link de download.';
      setErrorMessage(message);
    }
  };

  const handleDelete = async (
    document: PatientDocument,
    hard = false
  ) => {
    setErrorMessage(null);
    setFeedbackMessage(null);
    setActionState({ deletingId: document.id });
    try {
      await deleteMutation.mutateAsync({
        appointmentId,
        documentId: document.id,
        hard,
        tenantId,
      });
      setFeedbackMessage(
        hard
          ? 'Documento removido definitivamente.'
          : 'Documento removido com sucesso.'
      );
    } catch (deleteError) {
      const message =
        deleteError instanceof Error
          ? deleteError.message
          : 'Não foi possível remover o documento.';
      setErrorMessage(message);
    } finally {
      setActionState({ deletingId: null });
    }
  };

  const renderDocumentRow = (document: PatientDocument) => {
    const isDeleting = deletingId === document.id && deleteMutation.isPending;
    return (
      <div
        key={document.id}
        className="flex flex-col gap-2 rounded-lg border border-gray-200 p-4 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <p className="text-sm font-medium text-gray-900">
            {document.file_name}
          </p>
          <p className="text-xs text-gray-500">
            {formatBytes(document.file_size)} •{' '}
            <span
              className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${resolveStatusBadge(
                document.status
              )}`}
            >
              {document.status === 'uploaded'
                ? 'Disponível'
                : document.status === 'deleted'
                ? 'Removido'
                : document.status === 'failed'
                ? 'Falhou'
                : 'Pendente'}
            </span>
          </p>
          {document.uploaded_at ? (
            <p className="text-xs text-gray-500">
              Enviado em {formatDate(document.uploaded_at)}
            </p>
          ) : null}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => handleDownload(document)}
            className="rounded-md border border-gray-300 px-3 py-1 text-xs font-medium text-gray-700 transition hover:bg-gray-100"
            disabled={document.status !== 'uploaded'}
          >
            Download
          </button>
          {canManage && document.status !== 'deleted' ? (
            <>
              <button
                type="button"
                onClick={() => handleDelete(document, false)}
                className="rounded-md border border-gray-300 px-3 py-1 text-xs font-medium text-gray-700 transition hover:bg-gray-100"
                disabled={isDeleting}
              >
                {isDeleting && !deleteMutation.variables?.hard
                  ? 'Removendo...'
                  : 'Excluir'}
              </button>
              <button
                type="button"
                onClick={() => handleDelete(document, true)}
                className="rounded-md border border-red-200 px-3 py-1 text-xs font-medium text-red-700 transition hover:bg-red-50"
                disabled={isDeleting}
              >
                {isDeleting && deleteMutation.variables?.hard
                  ? 'Removendo...'
                  : 'Excluir definitivamente'}
              </button>
            </>
          ) : null}
        </div>
      </div>
    );
  };

  return (
    <section className="space-y-4">
      <header>
        <h3 className="text-sm font-semibold text-gray-900">Documentos</h3>
        <p className="text-xs text-gray-500">
          {canManage
            ? 'Envie pedidos médicos, guias ou imagens relevantes (máx. 10 MB).'
            : 'Visualização dos documentos anexados ao agendamento.'}
        </p>
      </header>

      {canManage ? (
        <div
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          className={`flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-6 text-center transition ${
            isDragging ? 'border-blue-400 bg-blue-50' : 'border-gray-200'
          } ${uploadMutation.isPending ? 'opacity-70' : ''}`}
        >
          <p className="text-sm text-gray-700">
            Arraste e solte arquivos aqui ou
          </p>
          <button
            type="button"
            onClick={handleOpenFileDialog}
            className="rounded-md bg-blue-600 px-3 py-1 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700"
            disabled={uploadMutation.isPending}
          >
            Selecionar arquivos
          </button>
          <p className="text-xs text-gray-500">
            Tipos aceitos: {allowedTypesDescription}. Tamanho máximo 10 MB.
          </p>
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            multiple
            onChange={onInputChange}
            accept={ALLOWED_EXTENSIONS.map((ext) => `.${ext}`).join(',')}
          />
        </div>
      ) : null}

      {feedbackMessage ? (
        <div className="rounded-md border border-green-100 bg-green-50 p-3 text-xs text-green-800">
          {feedbackMessage}
        </div>
      ) : null}

      {errorMessage || isError ? (
        <div className="rounded-md border border-red-100 bg-red-50 p-3 text-xs text-red-700">
          {errorMessage || error?.message || 'Não foi possível carregar os documentos.'}
        </div>
      ) : null}

      {isLoading ? (
        <p className="text-sm text-gray-500">Carregando documentos...</p>
      ) : null}

      {!isLoading && documents.length === 0 ? (
        <p className="text-sm text-gray-500">
          Nenhum documento enviado para este agendamento.
        </p>
      ) : null}

      {documents.length > 0 ? (
        <div className="space-y-3">
          {documents.map((document) => renderDocumentRow(document))}
        </div>
      ) : null}
    </section>
  );
}
