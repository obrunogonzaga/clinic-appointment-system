import { Dialog, Transition } from '@headlessui/react';
import {
  ArrowDownTrayIcon,
  CloudArrowUpIcon,
  DocumentIcon,
  ExclamationTriangleIcon,
  TrashIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { Fragment, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { Appointment } from '../types/appointment';
import type { PatientDocument } from '../types/patientDocument';
import { appointmentAPI } from '../services/api';

interface AppointmentDetailDrawerProps {
  appointment: Appointment | null;
  isOpen: boolean;
  onClose: () => void;
}

const role = (import.meta.env.VITE_API_USER_ROLE ?? 'admin').toLowerCase();
const maxUploadMb = Number(import.meta.env.VITE_PATIENT_DOCS_MAX_MB ?? 10);
const allowedMime = (import.meta.env.VITE_PATIENT_DOCS_ALLOWED_MIME ?? 'application/pdf,image/jpeg,image/png,image/webp,image/heic')
  .split(',')
  .map((mime) => mime.trim());

const formatBytes = (size: number): string => {
  if (!size) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const index = Math.min(Math.floor(Math.log(size) / Math.log(1024)), units.length - 1);
  const value = size / Math.pow(1024, index);
  return `${value.toFixed(value >= 10 || index === 0 ? 0 : 1)} ${units[index]}`;
};

const formatDateTime = (value?: string | null): string => {
  if (!value) return '-';
  try {
    const date = new Date(value);
    return date.toLocaleString('pt-BR');
  } catch {
    return value;
  }
};

const derivePatientId = (appointment: Appointment): string => {
  const cpf = appointment.documento_normalizado?.cpf || appointment.cpf;
  if (cpf) {
    return cpf.replace(/[^0-9a-zA-Z]/g, '');
  }

  return appointment.nome_paciente
    .normalize('NFD')
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .toLowerCase();
};

export const AppointmentDetailDrawer: React.FC<AppointmentDetailDrawerProps> = ({
  appointment,
  isOpen,
  onClose,
}) => {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [workingDocumentId, setWorkingDocumentId] = useState<string | null>(null);

  const appointmentId = appointment?.id;

  const documentsQuery = useQuery({
    queryKey: ['appointmentDocuments', appointmentId],
    queryFn: () => appointmentAPI.getAppointmentDocuments(appointmentId!),
    enabled: isOpen && Boolean(appointmentId),
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    if (!isOpen) {
      setErrorMessage(null);
      setSuccessMessage(null);
      setIsDragging(false);
      setWorkingDocumentId(null);
    }
  }, [isOpen]);

  const documents = useMemo<PatientDocument[]>(() => {
    return documentsQuery.data?.documents ?? [];
  }, [documentsQuery.data]);

  const handleFiles = useCallback(
    async (files: FileList | File[]) => {
      if (!appointment) {
        return;
      }

      const patientId = derivePatientId(appointment);

      setErrorMessage(null);
      setSuccessMessage(null);
      setIsUploading(true);

      for (const file of Array.from(files)) {
        if (file.size > maxUploadMb * 1024 * 1024) {
          setErrorMessage(
            `Arquivo "${file.name}" excede o limite de ${maxUploadMb}MB.`
          );
          continue;
        }

        const contentType = file.type || 'application/octet-stream';

        try {
          const presign = await appointmentAPI.presignDocumentUpload(
            appointment.id,
            {
              patient_id: patientId,
              file_name: file.name,
              content_type: contentType,
              file_size: file.size,
            }
          );

          const uploadResponse = await fetch(presign.upload_url, {
            method: 'PUT',
            headers: {
              'Content-Type': contentType,
              ...presign.headers,
            },
            body: file,
          });

          if (!uploadResponse.ok) {
            throw new Error(
              `Falha ao enviar arquivo (${uploadResponse.status})`
            );
          }

          const etag =
            uploadResponse.headers.get('ETag') ??
            uploadResponse.headers.get('etag') ??
            undefined;

          await appointmentAPI.confirmDocumentUpload(
            appointment.id,
            presign.document_id,
            {
              file_size: file.size,
              etag,
            }
          );

          setSuccessMessage(`Upload de "${file.name}" concluído.`);
          await documentsQuery.refetch();
        } catch (error) {
          console.error(error);
          setErrorMessage(
            error instanceof Error
              ? error.message
              : `Falha no upload de "${file.name}".`
          );
        }
      }

      setIsUploading(false);
    },
    [appointment, documentsQuery]
  );

  const handleInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const files = event.target.files;
      if (files) {
        void handleFiles(files);
        event.target.value = '';
      }
    },
    [handleFiles]
  );

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setIsDragging(false);
      if (event.dataTransfer.files?.length) {
        void handleFiles(event.dataTransfer.files);
      }
    },
    [handleFiles]
  );

  const handleDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDownload = useCallback(
    async (document: PatientDocument) => {
      if (!appointment) return;
      setWorkingDocumentId(document.id);
      try {
        const download = await appointmentAPI.getDocumentDownloadUrl(
          appointment.id,
          document.id
        );
        window.open(download.url, '_blank', 'noopener');
      } catch (error) {
        console.error(error);
        setErrorMessage('Não foi possível gerar o link de download.');
      } finally {
        setWorkingDocumentId(null);
      }
    },
    [appointment]
  );

  const handleDelete = useCallback(
    async (document: PatientDocument, hard = false) => {
      if (!appointment) return;

      if (
        hard &&
        !confirm('Tem certeza que deseja remover permanentemente este documento?')
      ) {
        return;
      }

      setWorkingDocumentId(document.id);
      setErrorMessage(null);
      setSuccessMessage(null);

      try {
        await appointmentAPI.deleteDocument(
          appointment.id,
          document.id,
          hard
        );
        setSuccessMessage('Documento removido com sucesso.');
        await documentsQuery.refetch();
      } catch (error) {
        console.error(error);
        setErrorMessage(
          hard
            ? 'Falha ao remover permanentemente o documento.'
            : 'Falha ao remover o documento.'
        );
      } finally {
        setWorkingDocumentId(null);
      }
    },
    [appointment, documentsQuery]
  );

  if (!appointment) {
    return null;
  }

  const canHardDelete = role === 'admin';

  return (
    <Transition show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/30" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
              <Transition.Child
                as={Fragment}
                enter="transform transition ease-in-out duration-300"
                enterFrom="translate-x-full"
                enterTo="translate-x-0"
                leave="transform transition ease-in-out duration-300"
                leaveFrom="translate-x-0"
                leaveTo="translate-x-full"
              >
                <Dialog.Panel className="pointer-events-auto w-screen max-w-2xl">
                  <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">
                    <div className="px-6 py-4 border-b border-gray-200 flex items-start justify-between">
                      <div>
                        <Dialog.Title className="text-lg font-semibold text-gray-900">
                          {appointment.nome_paciente}
                        </Dialog.Title>
                        <p className="text-sm text-gray-500 mt-1">
                          {appointment.nome_unidade} • {appointment.nome_marca}
                        </p>
                        <p className="text-sm text-gray-500">
                          {new Date(appointment.data_agendamento).toLocaleDateString('pt-BR')} às {appointment.hora_agendamento}
                        </p>
                      </div>
                      <button
                        type="button"
                        className="rounded-md text-gray-400 hover:text-gray-500"
                        onClick={onClose}
                      >
                        <span className="sr-only">Fechar</span>
                        <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                      </button>
                    </div>

                    <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
                      <h3 className="text-sm font-medium text-gray-700">Informações do agendamento</h3>
                      <dl className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-600">
                        <div>
                          <dt className="font-medium text-gray-500">Convênio</dt>
                          <dd>
                            {appointment.nome_convenio
                              ? `${appointment.nome_convenio}${appointment.numero_convenio ? ` • ${appointment.numero_convenio}` : ''}`
                              : '-'}
                          </dd>
                        </div>
                        <div>
                          <dt className="font-medium text-gray-500">Status</dt>
                          <dd>{appointment.status}</dd>
                        </div>
                        <div>
                          <dt className="font-medium text-gray-500">Telefone</dt>
                          <dd>{appointment.telefone || '-'}</dd>
                        </div>
                        <div>
                          <dt className="font-medium text-gray-500">Endereço</dt>
                          <dd>
                            {appointment.endereco_normalizado?.rua
                              ? `${appointment.endereco_normalizado.rua}${appointment.endereco_normalizado.numero ? `, ${appointment.endereco_normalizado.numero}` : ''}`
                              : appointment.endereco_coleta || '-'}
                          </dd>
                        </div>
                      </dl>
                    </div>

                    <div className="px-6 py-6 flex-1 overflow-y-auto">
                      <section>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <DocumentIcon className="h-5 w-5 text-indigo-600" />
                            <h3 className="text-base font-semibold text-gray-900">Documentos do paciente</h3>
                          </div>
                          <button
                            type="button"
                            onClick={() => inputRef.current?.click()}
                            className="inline-flex items-center space-x-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                            disabled={isUploading}
                          >
                            <CloudArrowUpIcon className="h-4 w-4" />
                            <span>Enviar arquivo</span>
                          </button>
                        </div>
                        <p className="mt-2 text-sm text-gray-500">
                          Tipos permitidos: {allowedMime.join(', ')} • Até {maxUploadMb}MB por arquivo.
                        </p>

                        <div
                          className={`mt-4 border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                            isDragging
                              ? 'border-indigo-400 bg-indigo-50'
                              : 'border-gray-300 bg-white'
                          } ${isUploading ? 'opacity-70' : ''}`}
                          onDragOver={handleDragOver}
                          onDragLeave={handleDragLeave}
                          onDrop={handleDrop}
                        >
                          <input
                            ref={inputRef}
                            type="file"
                            multiple
                            className="hidden"
                            onChange={handleInputChange}
                            accept={allowedMime.join(',')}
                          />
                          <p className="text-sm text-gray-700">
                            Arraste e solte arquivos aqui ou
                            <button
                              type="button"
                              onClick={() => inputRef.current?.click()}
                              className="text-indigo-600 font-medium ml-1 hover:underline"
                              disabled={isUploading}
                            >
                              clique para selecionar
                            </button>
                          </p>
                          {isUploading && (
                            <p className="mt-2 text-sm text-indigo-600">Enviando arquivos...</p>
                          )}
                        </div>

                        {errorMessage && (
                          <div className="mt-4 flex items-start space-x-2 rounded-md bg-red-50 p-3 text-sm text-red-700">
                            <ExclamationTriangleIcon className="h-5 w-5 flex-shrink-0" />
                            <p>{errorMessage}</p>
                          </div>
                        )}

                        {successMessage && (
                          <div className="mt-4 rounded-md bg-green-50 p-3 text-sm text-green-700">
                            {successMessage}
                          </div>
                        )}

                        <div className="mt-6">
                          {documentsQuery.isLoading ? (
                            <p className="text-sm text-gray-500">Carregando documentos...</p>
                          ) : documents.length === 0 ? (
                            <p className="text-sm text-gray-500">
                              Nenhum documento disponível para este agendamento.
                            </p>
                          ) : (
                            <ul className="space-y-3">
                              {documents.map((document) => (
                                <li
                                  key={document.id}
                                  className="flex items-start justify-between rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
                                >
                                  <div>
                                    <p className="font-medium text-gray-900">
                                      {document.original_file_name}
                                      {document.status !== 'available' && (
                                        <span className="ml-2 inline-flex items-center rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-semibold text-yellow-800">
                                          {document.status.replace('_', ' ')}
                                        </span>
                                      )}
                                    </p>
                                    <p className="text-sm text-gray-500">
                                      {formatBytes(document.file_size)} • Upload em {formatDateTime(document.uploaded_at ?? document.created_at)}
                                    </p>
                                    {document.uploader_user_id && (
                                      <p className="text-xs text-gray-400">
                                        Enviado por: {document.uploader_user_id}
                                        {document.source_ip ? ` • IP ${document.source_ip}` : ''}
                                      </p>
                                    )}
                                  </div>
                                  <div className="flex items-center space-x-2">
                                    <button
                                      type="button"
                                      className="inline-flex items-center rounded-md border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
                                      onClick={() => void handleDownload(document)}
                                      disabled={workingDocumentId === document.id}
                                    >
                                      <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                                      Download
                                    </button>
                                    <button
                                      type="button"
                                      className="inline-flex items-center rounded-md border border-red-200 bg-white px-3 py-2 text-sm font-medium text-red-600 shadow-sm hover:bg-red-50"
                                      onClick={() => void handleDelete(document, false)}
                                      disabled={workingDocumentId === document.id}
                                    >
                                      <TrashIcon className="h-4 w-4 mr-1" />
                                      Excluir
                                    </button>
                                    {canHardDelete && (
                                      <button
                                        type="button"
                                        className="inline-flex items-center rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 shadow-sm hover:bg-red-100"
                                        onClick={() => void handleDelete(document, true)}
                                        disabled={workingDocumentId === document.id}
                                      >
                                        <TrashIcon className="h-4 w-4 mr-1" />
                                        Excluir definitivamente
                                      </button>
                                    )}
                                  </div>
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      </section>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default AppointmentDetailDrawer;
