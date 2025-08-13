import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { CloudArrowUpIcon, DocumentIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { appointmentAPI } from '../services/api';
import type { ExcelUploadResponse } from '../types/appointment';

interface FileUploadProps {
  onUploadSuccess: (result: ExcelUploadResponse) => void;
  onUploadError: (error: string) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess, onUploadError }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [replaceExisting, setReplaceExisting] = useState(false);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      
      // Validate file type
      const allowedTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
        'application/vnd.ms-excel', // .xls
        'text/csv' // .csv
      ];
      
      if (!allowedTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls|csv)$/i)) {
        onUploadError('Formato de arquivo não suportado. Use .xlsx, .xls ou .csv');
        return;
      }

      // Validate file size (10MB max)
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        onUploadError('Arquivo muito grande. Tamanho máximo: 10MB');
        return;
      }

      setIsUploading(true);
      setUploadProgress(0);

      try {
        // Simulate progress
        const progressInterval = setInterval(() => {
          setUploadProgress((prev) => {
            if (prev >= 90) {
              clearInterval(progressInterval);
              return prev;
            }
            return prev + 10;
          });
        }, 200);

        const result = await appointmentAPI.uploadExcel(file, replaceExisting);
        
        clearInterval(progressInterval);
        setUploadProgress(100);
        
        setTimeout(() => {
          onUploadSuccess(result);
          setIsUploading(false);
          setUploadProgress(0);
        }, 500);
        
      } catch (error: any) {
        setIsUploading(false);
        setUploadProgress(0);
        
        const errorMessage = error.response?.data?.detail || 
                           error.message || 
                           'Erro ao fazer upload do arquivo';
        onUploadError(errorMessage);
      }
    },
    [replaceExisting, onUploadSuccess, onUploadError]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    maxFiles: 1,
    disabled: isUploading
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-10 text-center transition-all duration-200 cursor-pointer
          ${isDragActive && !isDragReject ? 'border-blue-500 bg-blue-50 scale-105' : ''}
          ${isDragReject ? 'border-red-500 bg-red-50' : ''}
          ${!isDragActive && !isDragReject ? 'border-gray-300 hover:border-gray-400 hover:bg-gray-50' : ''}
          ${isUploading ? 'cursor-not-allowed opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          {isUploading ? (
            <>
              <DocumentIcon className="w-16 h-16 text-blue-500 animate-pulse" />
              <div className="w-full max-w-xs bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-sm text-gray-600">
                Processando arquivo... {uploadProgress}%
              </p>
            </>
          ) : (
            <>
              {isDragReject ? (
                <ExclamationTriangleIcon className="w-12 h-12 text-red-500" />
              ) : (
                <CloudArrowUpIcon className="w-16 h-16 text-gray-400" />
              )}
              
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? 'Solte o arquivo aqui' : 'Arraste o arquivo Excel aqui'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  ou clique para selecionar
                </p>
              </div>
              
              <p className="text-xs text-gray-400">
                Formatos suportados: .xlsx, .xls, .csv (máx. 10MB)
              </p>
            </>
          )}
        </div>
      </div>

      {/* Replace existing option */}
      <div className="mt-4 flex items-center">
        <input
          id="replace-existing"
          type="checkbox"
          checked={replaceExisting}
          onChange={(e) => setReplaceExisting(e.target.checked)}
          disabled={isUploading}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="replace-existing" className="ml-2 block text-sm text-gray-700">
          Substituir agendamentos existentes das mesmas unidades
        </label>
      </div>
    </div>
  );
};