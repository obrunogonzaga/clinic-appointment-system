import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    PlusIcon,
    UserIcon,
    XCircleIcon
} from '@heroicons/react/24/outline';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import React, { useState } from 'react';
import { CollectorFilters } from '../components/CollectorFilters';
import { CollectorForm } from '../components/CollectorForm';
import { CollectorTable } from '../components/CollectorTable';
import { collectorAPI } from '../services/api';
import type {
    Collector,
    CollectorCreateRequest,
    CollectorFilter,
    CollectorFormData,
    CollectorUpdateRequest
} from '../types/collector';

export const CollectorsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<CollectorFilter>({
    page: 1,
    page_size: 50
  });
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedCollector, setSelectedCollector] = useState<Collector | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  // Fetch collectors
  const { 
    data: collectorsData, 
    isLoading: isLoadingCollectors
  } = useQuery({
    queryKey: ['collectors', filters],
    queryFn: () => collectorAPI.getCollectors(filters),
    refetchOnWindowFocus: false,
  });

  // Fetch collector stats
  const { 
    data: collectorStats, 
    isLoading: isLoadingStats 
  } = useQuery({
    queryKey: ['collectorStats'],
    queryFn: () => collectorAPI.getCollectorStats(),
    refetchOnWindowFocus: false,
  });

  // Create collector mutation
  const createCollectorMutation = useMutation({
    mutationFn: (data: CollectorCreateRequest) => collectorAPI.createCollector(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collectors'] });
      queryClient.invalidateQueries({ queryKey: ['collectorStats'] });
      setIsFormOpen(false);
      setError(null);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.response?.data?.message || 'Erro ao criar coletora';
      setFormError(message);
      setError(message);
    }
  });

  // Update collector mutation
  const updateCollectorMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: CollectorUpdateRequest }) => 
      collectorAPI.updateCollector(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collectors'] });
      queryClient.invalidateQueries({ queryKey: ['collectorStats'] });
      setIsFormOpen(false);
      setSelectedCollector(undefined);
      setError(null);
      setFormError(null);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.response?.data?.message || 'Erro ao atualizar coletora';
      setFormError(message);
      setError(message);
    }
  });

  // Delete collector mutation
  const deleteCollectorMutation = useMutation({
    mutationFn: (id: string) => collectorAPI.deleteCollector(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collectors'] });
      queryClient.invalidateQueries({ queryKey: ['collectorStats'] });
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Erro ao excluir coletora');
    }
  });

  // Update collector status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => 
      collectorAPI.updateCollectorStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collectors'] });
      queryClient.invalidateQueries({ queryKey: ['collectorStats'] });
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Erro ao atualizar status');
    }
  });

  const handleFormSubmit = (data: CollectorFormData) => {
    const requestData = {
      ...data,
      data_nascimento: data.data_nascimento || undefined,
    };

    setFormError(null);
    setError(null);

    if (selectedCollector) {
      updateCollectorMutation.mutate({ id: selectedCollector.id, data: requestData });
    } else {
      createCollectorMutation.mutate(requestData);
    }
  };

  const handleEdit = (collector: Collector) => {
    setSelectedCollector(collector);
    setIsFormOpen(true);
    setFormError(null);
  };

  const handleStatusChange = (id: string, status: string) => {
    updateStatusMutation.mutate({ id, status });
  };

  const handleDelete = (id: string) => {
    if (!window.confirm('Tem certeza que deseja excluir esta coletora?')) {
      return;
    }

    deleteCollectorMutation.mutate(id);
  };

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({
      ...prev,
      page: newPage
    }));
  };

  const handleNewCollector = () => {
    setSelectedCollector(undefined);
    setIsFormOpen(true);
    setFormError(null);
    setError(null);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setSelectedCollector(undefined);
    setError(null);
    setFormError(null);
  };

  const stats = collectorStats?.stats || {
    total_collectors: 0,
    active_collectors: 0,
    inactive_collectors: 0,
    suspended_collectors: 0
  };

  const isFormLoading = createCollectorMutation.isPending || updateCollectorMutation.isPending;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900">
                Gerenciamento de Coletoras
              </h1>
              <p className="text-gray-600 mt-3 text-lg">
                Cadastre e gerencie coletoras para coletas domiciliares
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleNewCollector}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                Nova Coletora
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
                  {isLoadingStats ? '...' : stats.total_collectors}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <CheckCircleIcon className="w-10 h-10 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Ativas</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.active_collectors}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <XCircleIcon className="w-10 h-10 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Inativas</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.inactive_collectors}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="w-10 h-10 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Suspensas</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isLoadingStats ? '...' : stats.suspended_collectors}
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
        <CollectorFilters
          onFilterChange={setFilters}
          isLoading={isLoadingCollectors}
        />

        {/* Collectors Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Coletoras</h2>
              
              {collectorsData?.pagination && (
                <div className="text-sm text-gray-500">
                  Mostrando {collectorsData.collectors.length} de {collectorsData.pagination.total_items} coletoras
                </div>
              )}
            </div>

            <CollectorTable
              collectors={collectorsData?.collectors || []}
              isLoading={isLoadingCollectors}
              onStatusChange={handleStatusChange}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />

            {/* Pagination */}
            {collectorsData?.pagination && collectorsData.pagination.total_pages > 1 && (
              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-gray-500">
                  Página {collectorsData.pagination.page} de {collectorsData.pagination.total_pages}
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => handlePageChange(collectorsData.pagination.page - 1)}
                    disabled={!collectorsData.pagination.has_previous}
                    className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  
                  <button
                    onClick={() => handlePageChange(collectorsData.pagination.page + 1)}
                    disabled={!collectorsData.pagination.has_next}
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

      {/* Collector Form Modal */}
      <CollectorForm
        collector={selectedCollector}
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        onSubmit={handleFormSubmit}
        isLoading={isFormLoading}
        serverError={formError ?? undefined}
        onServerErrorClear={() => setFormError(null)}
      />
    </div>
  );
};
