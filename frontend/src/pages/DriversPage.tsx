import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    PlusIcon,
    UserIcon,
    XCircleIcon
} from '@heroicons/react/24/outline';
import { isAxiosError } from 'axios';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import React, { useState } from 'react';
import { DriverFilters } from '../components/DriverFilters';
import { DriverForm } from '../components/DriverForm';
import { DriverTable } from '../components/DriverTable';
import { driverAPI } from '../services/api';
import type {
    Driver,
    DriverCreateRequest,
    DriverFilter,
    DriverFormData,
    DriverUpdateRequest
} from '../types/driver';

const getErrorMessage = (error: unknown, fallback: string): string => {
  if (isAxiosError<{ detail?: string; message?: string }>(error)) {
    return error.response?.data?.detail || error.response?.data?.message || fallback;
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallback;
};

export const DriversPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<DriverFilter>({
    page: 1,
    page_size: 50
  });
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedDriver, setSelectedDriver] = useState<Driver | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [reportDate, setReportDate] = useState<string>(new Date().toISOString().slice(0, 10)); // YYYY-MM-DD
  const [reportDriverId, setReportDriverId] = useState<string>('');

  // Fetch drivers
  const { 
    data: driversData, 
    isLoading: isLoadingDrivers
  } = useQuery({
    queryKey: ['drivers', filters],
    queryFn: () => driverAPI.getDrivers(filters),
    refetchOnWindowFocus: false,
  });

  // Fetch driver stats
  const { 
    data: driverStats, 
    isLoading: isLoadingStats 
  } = useQuery({
    queryKey: ['driverStats'],
    queryFn: () => driverAPI.getDriverStats(),
    refetchOnWindowFocus: false,
  });

  // Create driver mutation
  const createDriverMutation = useMutation({
    mutationFn: (data: DriverCreateRequest) => driverAPI.createDriver(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
      queryClient.invalidateQueries({ queryKey: ['driverStats'] });
      setIsFormOpen(false);
      setError(null);
    },
    onError: (error: unknown) => {
      setError(getErrorMessage(error, 'Erro ao criar motorista'));
    }
  });

  // Update driver mutation
  const updateDriverMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: DriverUpdateRequest }) => 
      driverAPI.updateDriver(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
      queryClient.invalidateQueries({ queryKey: ['driverStats'] });
      setIsFormOpen(false);
      setSelectedDriver(undefined);
      setError(null);
    },
    onError: (error: unknown) => {
      setError(getErrorMessage(error, 'Erro ao atualizar motorista'));
    }
  });

  // Delete driver mutation
  const deleteDriverMutation = useMutation({
    mutationFn: (id: string) => driverAPI.deleteDriver(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
      queryClient.invalidateQueries({ queryKey: ['driverStats'] });
    },
    onError: (error: unknown) => {
      setError(getErrorMessage(error, 'Erro ao excluir motorista'));
    }
  });

  // Update driver status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => 
      driverAPI.updateDriverStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
      queryClient.invalidateQueries({ queryKey: ['driverStats'] });
    },
    onError: (error: unknown) => {
      setError(getErrorMessage(error, 'Erro ao atualizar status'));
    }
  });

  const handleFormSubmit = (data: DriverFormData) => {
    const requestData = {
      ...data,
      data_nascimento: data.data_nascimento || undefined,
    };

    if (selectedDriver) {
      updateDriverMutation.mutate({ id: selectedDriver.id, data: requestData });
    } else {
      createDriverMutation.mutate(requestData);
    }
  };

  const handleEdit = (driver: Driver) => {
    setSelectedDriver(driver);
    setIsFormOpen(true);
  };

  const handleStatusChange = (id: string, status: string) => {
    updateStatusMutation.mutate({ id, status });
  };

  const handleDelete = (id: string) => {
    if (!window.confirm('Tem certeza que deseja excluir este motorista?')) {
      return;
    }

    deleteDriverMutation.mutate(id);
  };

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({
      ...prev,
      page: newPage
    }));
  };

  const handleNewDriver = () => {
    setSelectedDriver(undefined);
    setIsFormOpen(true);
  };

  const handleGenerateRoute = async () => {
    try {
      if (!driversData || driversData.drivers.length === 0) {
        alert('Não há motoristas na lista para selecionar.');
        return;
      }
      const driver = selectedDriver
        ? selectedDriver
        : (driversData.drivers.find(d => d.id === reportDriverId) || driversData.drivers[0]);
      const date = reportDate || new Date().toISOString().slice(0, 10);
      const url = `/#/routes/driver?driverId=${encodeURIComponent(driver.id)}&date=${encodeURIComponent(date)}`;
      window.open(url, '_blank');
    } catch (error: unknown) {
      console.error('Erro ao abrir página de rota:', error);
      alert('Erro ao abrir página de rota');
    }
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setSelectedDriver(undefined);
    setError(null);
  };

  const stats = driverStats?.stats || {
    total_drivers: 0,
    active_drivers: 0,
    inactive_drivers: 0,
    suspended_drivers: 0
  };

  const isFormLoading = createDriverMutation.isPending || updateDriverMutation.isPending;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900">
                Gerenciamento de Motoristas
              </h1>
              <p className="text-gray-600 mt-3 text-lg">
                Cadastre e gerencie motoristas para coletas domiciliares
              </p>
            </div>
            <div className="flex items-center gap-3">
              {/* Seletor de motorista (quando nenhum está selecionado para edição) */}
              {driversData?.drivers?.length ? (
                <select
                  value={reportDriverId}
                  onChange={(e) => setReportDriverId(e.target.value)}
                  className="px-3 py-2 text-sm border border-gray-300 rounded-md bg-white"
                  title="Escolha o motorista para o relatório"
                >
                  <option value="">(usar selecionado ou primeiro)</option>
                  {driversData.drivers.map((d) => (
                    <option key={d.id} value={d.id}>{d.nome_completo}</option>
                  ))}
                </select>
              ) : null}

              {/* Data do relatório */}
              <input
                type="date"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
                className="px-3 py-2 text-sm border border-gray-300 rounded-md bg-white"
                title="Data do relatório"
              />

              <button
                onClick={handleGenerateRoute}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Gerar Rota
              </button>
              <button
                onClick={handleNewDriver}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                Novo Motorista
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <UserIcon className="w-10 h-10 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.total_drivers}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <CheckCircleIcon className="w-10 h-10 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Ativos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.active_drivers}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <XCircleIcon className="w-10 h-10 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Inativos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.inactive_drivers}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="w-10 h-10 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Suspensos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.suspended_drivers}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <XCircleIcon className="w-5 h-5 text-red-600 mr-2" />
              <p className="font-medium text-red-800">{error}</p>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-600 hover:text-red-800"
              >
                <XCircleIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Filters */}
        <DriverFilters
          onFilterChange={setFilters}
          isLoading={isLoadingDrivers}
        />

        {/* Drivers Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Motoristas</h2>
              
              {driversData?.pagination && (
                <div className="text-sm text-gray-500">
                  Mostrando {driversData.drivers.length} de {driversData.pagination.total_items} motoristas
                </div>
              )}
            </div>

            <DriverTable
              drivers={driversData?.drivers || []}
              isLoading={isLoadingDrivers}
              onStatusChange={handleStatusChange}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />

            {/* Pagination */}
            {driversData?.pagination && driversData.pagination.total_pages > 1 && (
              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-gray-500">
                  Página {driversData.pagination.page} de {driversData.pagination.total_pages}
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => handlePageChange(driversData.pagination.page - 1)}
                    disabled={!driversData.pagination.has_previous}
                    className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  
                  <button
                    onClick={() => handlePageChange(driversData.pagination.page + 1)}
                    disabled={!driversData.pagination.has_next}
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

      {/* Driver Form Modal */}
      <DriverForm
        driver={selectedDriver}
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        onSubmit={handleFormSubmit}
        isLoading={isFormLoading}
      />
    </div>
  );
};