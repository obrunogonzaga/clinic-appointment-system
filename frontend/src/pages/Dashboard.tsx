import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { 
  CalendarDaysIcon, 
  DocumentArrowUpIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  BuildingOfficeIcon,
  TagIcon
} from '@heroicons/react/24/outline';
import { FileUpload } from '../components/FileUpload';
import { AppointmentFilters } from '../components/AppointmentFilters';
import { AppointmentTable } from '../components/AppointmentTable';
import { appointmentAPI } from '../services/api';
import type { AppointmentFilter, ExcelUploadResponse } from '../types/appointment';

export const Dashboard: React.FC = () => {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<AppointmentFilter>({
    page: 1,
    page_size: 50
  });
  const [uploadResult, setUploadResult] = useState<ExcelUploadResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Fetch appointments
  const { 
    data: appointmentsData, 
    isLoading: isLoadingAppointments
  } = useQuery({
    queryKey: ['appointments', filters],
    queryFn: () => appointmentAPI.getAppointments(filters),
    refetchOnWindowFocus: false,
  });

  // Fetch filter options
  const { 
    data: filterOptions, 
    isLoading: isLoadingFilters 
  } = useQuery({
    queryKey: ['filterOptions'],
    queryFn: () => appointmentAPI.getFilterOptions(),
    refetchOnWindowFocus: false,
  });

  // Fetch dashboard stats
  const { 
    data: dashboardStats, 
    isLoading: isLoadingStats 
  } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => appointmentAPI.getDashboardStats(),
    refetchOnWindowFocus: false,
  });

  const handleUploadSuccess = (result: ExcelUploadResponse) => {
    setUploadResult(result);
    setUploadError(null);
    
    // Refresh data after successful upload
    queryClient.invalidateQueries({ queryKey: ['appointments'] });
    queryClient.invalidateQueries({ queryKey: ['filterOptions'] });
    queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
    
    // Auto-hide success message after 5 seconds
    setTimeout(() => {
      setUploadResult(null);
    }, 5000);
  };

  const handleUploadError = (error: string) => {
    setUploadError(error);
    setUploadResult(null);
    
    // Auto-hide error message after 5 seconds
    setTimeout(() => {
      setUploadError(null);
    }, 5000);
  };

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await appointmentAPI.updateAppointmentStatus(id, status);
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
    } catch (error) {
      console.error('Error updating appointment status:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Tem certeza que deseja excluir este agendamento?')) {
      return;
    }

    try {
      await appointmentAPI.deleteAppointment(id);
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
    } catch (error) {
      console.error('Error deleting appointment:', error);
    }
  };

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({
      ...prev,
      page: newPage
    }));
  };

  const stats = dashboardStats?.stats || {
    total_appointments: 0,
    confirmed_appointments: 0,
    cancelled_appointments: 0,
    total_units: 0,
    total_brands: 0
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-4xl font-bold text-gray-900">
            Sistema de Agendamentos
          </h1>
          <p className="text-gray-600 mt-3 text-lg">
            Faça upload de arquivos Excel e gerencie agendamentos
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-10">
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <CalendarDaysIcon className="w-10 h-10 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.total_appointments}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <CheckCircleIcon className="w-10 h-10 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Confirmados</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.confirmed_appointments}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <XCircleIcon className="w-10 h-10 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Cancelados</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.cancelled_appointments}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <BuildingOfficeIcon className="w-10 h-10 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Unidades</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.total_units}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <TagIcon className="w-10 h-10 text-indigo-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Marcas</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.total_brands}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Upload Section */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-8">
          <div className="flex items-center space-x-2 mb-6">
            <DocumentArrowUpIcon className="w-6 h-6 text-gray-400" />
            <h2 className="text-xl font-semibold text-gray-900">Upload de Arquivo</h2>
          </div>
          
          <FileUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />

          {/* Upload Result Messages */}
          {uploadResult && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center">
                <CheckCircleIcon className="w-5 h-5 text-green-600 mr-2" />
                <div>
                  <p className="font-medium text-green-800">{uploadResult.message}</p>
                  <div className="text-sm text-green-600 mt-1">
                    <span>Total: {uploadResult.total_rows} | </span>
                    <span>Válidos: {uploadResult.valid_rows} | </span>
                    <span>Inválidos: {uploadResult.invalid_rows} | </span>
                    <span>Importados: {uploadResult.imported_appointments}</span>
                    {uploadResult.processing_time && (
                      <span> | Tempo: {uploadResult.processing_time.toFixed(1)}s</span>
                    )}
                  </div>
                  {uploadResult.errors.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm font-medium text-red-800">Erros encontrados:</p>
                      <ul className="text-sm text-red-600 mt-1 ml-4">
                        {uploadResult.errors.slice(0, 5).map((error, index) => (
                          <li key={index}>• {error}</li>
                        ))}
                        {uploadResult.errors.length > 5 && (
                          <li>• ... e mais {uploadResult.errors.length - 5} erros</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {uploadError && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center">
                <XCircleIcon className="w-5 h-5 text-red-600 mr-2" />
                <p className="font-medium text-red-800">{uploadError}</p>
              </div>
            </div>
          )}
        </div>

        {/* Filters */}
        <AppointmentFilters
          filters={filters}
          onFiltersChange={setFilters}
          units={filterOptions?.units || []}
          brands={filterOptions?.brands || []}
          statuses={filterOptions?.statuses || []}
          isLoading={isLoadingFilters}
        />

        {/* Appointments Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Agendamentos</h2>
              
              {appointmentsData?.pagination && (
                <div className="text-sm text-gray-500">
                  Mostrando {appointmentsData.appointments.length} de {appointmentsData.pagination.total_items} agendamentos
                </div>
              )}
            </div>

            <AppointmentTable
              appointments={appointmentsData?.appointments || []}
              isLoading={isLoadingAppointments}
              onStatusChange={handleStatusChange}
              onDelete={handleDelete}
            />

            {/* Pagination */}
            {appointmentsData?.pagination && appointmentsData.pagination.total_pages > 1 && (
              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-gray-500">
                  Página {appointmentsData.pagination.page} de {appointmentsData.pagination.total_pages}
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => handlePageChange(appointmentsData.pagination.page - 1)}
                    disabled={!appointmentsData.pagination.has_previous}
                    className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  
                  <button
                    onClick={() => handlePageChange(appointmentsData.pagination.page + 1)}
                    disabled={!appointmentsData.pagination.has_next}
                    className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Próximo
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};