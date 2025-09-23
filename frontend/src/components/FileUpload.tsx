import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  ArrowUpTrayIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { appointmentAPI } from '../services/api';
import type { ExcelUploadResponse } from '../types/appointment';
import { Modal } from './ui/Modal';

interface FileUploadProps {
  onUploadSuccess: (result: ExcelUploadResponse) => void;
  onUploadError: (error: string) => void;
  className?: string;
  buttonLabel?: string;
}

const ACCEPTED_TYPES = {
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-excel': ['.xls'],
  'text/csv': ['.csv'],
};

const MAX_SIZE_BYTES = 10 * 1024 * 1024; // 10MB

const hasFiles = (event: DragEvent): boolean => {
  const types = event.dataTransfer?.types;
  return Boolean(types && Array.from(types).includes('Files'));
};

export const FileUpload: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onUploadError,
  className = '',
  buttonLabel = 'Importar Excel',
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [replaceExisting, setReplaceExisting] = useState(false);
  const [isGlobalDragging, setIsGlobalDragging] = useState(false);
  const dragDepth = useRef(0);
  const progressIntervalRef = useRef<number | null>(null);

  const resetProgressInterval = useCallback(() => {
    if (progressIntervalRef.current) {
      window.clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
  }, []);

  const stopUploading = useCallback(() => {
    resetProgressInterval();
    setIsUploading(false);
    setUploadProgress(0);
  }, [resetProgressInterval]);

  const handleUpload = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0 || isUploading) {
      return;
    }

    const file = acceptedFiles[0];
    const fileExtensionIsValid = Object.values(ACCEPTED_TYPES)
      .flat()
      .some((extension) => file.name.toLowerCase().endsWith(extension));
    const fileTypeIsValid = Object.keys(ACCEPTED_TYPES).includes(file.type);

    if (!fileExtensionIsValid && !fileTypeIsValid) {
      onUploadError('Formato de arquivo não suportado. Use .xlsx, .xls ou .csv');
      return;
    }

    if (file.size > MAX_SIZE_BYTES) {
      onUploadError('Arquivo muito grande. Tamanho máximo: 10MB');
      return;
    }

    setIsModalOpen(true);
    setIsUploading(true);
    setUploadProgress(0);

    progressIntervalRef.current = window.setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          return prev;
        }
        return prev + 8;
      });
    }, 180);

    try {
      const result = await appointmentAPI.uploadExcel(file, replaceExisting);
      resetProgressInterval();
      setUploadProgress(100);

      setTimeout(() => {
        onUploadSuccess(result);
        stopUploading();
        setIsModalOpen(false);
      }, 400);
    } catch (error: unknown) {
      stopUploading();
      let errorMessage = 'Erro ao fazer upload do arquivo';

      if (typeof error === 'object' && error !== null && 'response' in error) {
        const responseError = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail;
        if (responseError) {
          errorMessage = responseError;
        }
      } else if (error instanceof Error && error.message) {
        errorMessage = error.message;
      }

      onUploadError(errorMessage);
    }
  }, [isUploading, onUploadError, onUploadSuccess, replaceExisting, resetProgressInterval, stopUploading]);

  const { getRootProps, getInputProps, isDragActive, isDragReject, open } = useDropzone({
    onDrop: handleUpload,
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
    disabled: isUploading,
    noClick: true,
    noKeyboard: true,
  });

  useEffect(() => {
    const handleDragEnter = (event: DragEvent) => {
      if (!hasFiles(event) || isUploading) {
        return;
      }
      event.preventDefault();
      dragDepth.current += 1;
      setIsGlobalDragging(true);
    };

    const handleDragOver = (event: DragEvent) => {
      if (!hasFiles(event)) {
        return;
      }
      event.preventDefault();
      event.dataTransfer!.dropEffect = isUploading ? 'none' : 'copy';
    };

    const handleDragLeave = (event: DragEvent) => {
      if (!hasFiles(event)) {
        return;
      }
      event.preventDefault();
      dragDepth.current = Math.max(dragDepth.current - 1, 0);
      if (dragDepth.current === 0) {
        setIsGlobalDragging(false);
      }
    };

    const handleDrop = (event: DragEvent) => {
      if (!hasFiles(event)) {
        return;
      }
      event.preventDefault();
      dragDepth.current = 0;
      setIsGlobalDragging(false);

      if (isUploading) {
        return;
      }

      const files = Array.from(event.dataTransfer?.files || []);
      if (files.length > 0) {
        void handleUpload(files);
      }
    };

    window.addEventListener('dragenter', handleDragEnter);
    window.addEventListener('dragover', handleDragOver);
    window.addEventListener('dragleave', handleDragLeave);
    window.addEventListener('drop', handleDrop);

    return () => {
      window.removeEventListener('dragenter', handleDragEnter);
      window.removeEventListener('dragover', handleDragOver);
      window.removeEventListener('dragleave', handleDragLeave);
      window.removeEventListener('drop', handleDrop);
    };
  }, [handleUpload, isUploading]);

  useEffect(() => {
    return () => {
      resetProgressInterval();
    };
  }, [resetProgressInterval]);

  const handleManualSelection = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files || event.target.files.length === 0) {
      return;
    }
    const files = Array.from(event.target.files);
    event.target.value = '';
    void handleUpload(files);
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setIsModalOpen(true)}
        disabled={isUploading}
        className={`inline-flex items-center justify-center rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:from-indigo-500 hover:to-purple-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:cursor-not-allowed disabled:opacity-70 ${className}`}
        aria-haspopup="dialog"
      >
        <DocumentTextIcon className="mr-2 h-5 w-5" />
        {buttonLabel}
      </button>

      {isGlobalDragging && (
        <div
          className="fixed inset-0 z-40 flex flex-col items-center justify-center bg-indigo-700/80 text-white backdrop-blur-sm transition-opacity"
          aria-hidden="true"
        >
          <CloudArrowUpIcon className="h-16 w-16 animate-bounce" />
          <p className="mt-4 text-xl font-semibold">Solte o arquivo para importar</p>
          <p className="mt-2 text-sm text-indigo-100">Formatos: .xlsx, .xls, .csv (máx. 10MB)</p>
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          if (!isUploading) {
            setIsModalOpen(false);
          }
        }}
        title="Importar agendamentos via Excel"
        size="lg"
      >
        <div
          {...getRootProps()}
          className={`
            mt-2 rounded-2xl border-2 border-dashed p-10 text-center transition
            ${isDragReject ? 'border-red-400 bg-red-50' : ''}
            ${isDragActive && !isDragReject ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200 bg-gray-50'}
            ${isUploading ? 'opacity-70' : ''}
          `}
          aria-label="Área de upload de arquivo"
        >
          <input
            {...getInputProps({ onChange: handleManualSelection })}
            aria-label="Selecione um arquivo de agendamentos"
          />

          <div className="flex flex-col items-center text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow">
              {isDragReject ? (
                <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
              ) : (
                <ArrowUpTrayIcon className="h-8 w-8 text-indigo-500" />
              )}
            </div>

            {isUploading ? (
              <>
                <p className="mt-4 text-base font-semibold text-gray-900">Processando arquivo...</p>
                <p className="mt-2 text-sm text-gray-600">Mantenha esta janela aberta até a conclusão.</p>
                <div className="mt-6 w-full max-w-md">
                  <div className="h-2 w-full rounded-full bg-gray-200">
                    <div
                      className="h-2 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 transition-all"
                      style={{ width: `${uploadProgress}%` }}
                      aria-valuenow={uploadProgress}
                      aria-valuemin={0}
                      aria-valuemax={100}
                    />
                  </div>
                  <p className="mt-2 text-sm text-gray-600">{uploadProgress}%</p>
                </div>
              </>
            ) : (
              <>
                <p className="mt-4 text-lg font-semibold text-gray-900">
                  Arraste o arquivo para cá ou
                  <button
                    type="button"
                    onClick={open}
                    className="ml-1 text-indigo-600 underline hover:text-indigo-700 focus:outline-none"
                  >
                    procure no computador
                  </button>
                </p>
                <p className="mt-2 text-sm text-gray-600">
                  Formatos suportados: .xlsx, .xls, .csv — limite de 10&nbsp;MB
                </p>
              </>
            )}
          </div>
        </div>

        <div className="mt-6 flex items-start space-x-3 text-left">
          <input
            id="replace-existing"
            type="checkbox"
            checked={replaceExisting}
            onChange={(event) => setReplaceExisting(event.target.checked)}
            disabled={isUploading}
            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <label htmlFor="replace-existing" className="text-sm text-gray-700">
            Substituir agendamentos existentes das mesmas unidades
          </label>
        </div>

        <div className="mt-6 text-sm text-gray-500">
          <p>O upload utiliza o mesmo fluxo atual da API. Certifique-se de que o arquivo está no formato correto.</p>
        </div>
      </Modal>
    </>
  );
};
