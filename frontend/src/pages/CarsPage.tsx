import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    PlusIcon,
    TruckIcon,
    XCircleIcon
} from '@heroicons/react/24/outline';
import { isAxiosError } from 'axios';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import React, { useState } from 'react';
import { CarFilters } from '../components/CarFilters';
import { CarForm } from '../components/CarForm';
import { CarTable } from '../components/CarTable';
import { carAPI } from '../services/api';
import type {
    Car,
    CarCreateRequest,
    CarFilter,
    CarFormData,
    CarUpdateRequest
} from '../types/car';

const getErrorMessage = (error: unknown, fallback: string): string => {
  if (isAxiosError<{ detail?: string; message?: string }>(error)) {
    return error.response?.data?.detail || error.response?.data?.message || fallback;
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallback;
};

export const CarsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<CarFilter>({
    page: 1,
    page_size: 50
  });
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedCar, setSelectedCar] = useState<Car | undefined>();
  const [error, setError] = useState<string | null>(null);

  // Fetch cars
  const { 
    data: carsData, 
    isLoading: isLoadingCars
  } = useQuery({
    queryKey: ['cars', filters],
    queryFn: () => carAPI.getCars(filters),
    refetchOnWindowFocus: false,
  });

  // Fetch car stats
  const { 
    data: carStats, 
    isLoading: isLoadingStats 
  } = useQuery({
    queryKey: ['carStats'],
    queryFn: () => carAPI.getCarStats(),
    refetchOnWindowFocus: false,
  });

  // Create car mutation
  const createCarMutation = useMutation({
    mutationFn: (data: CarCreateRequest) => carAPI.createCar(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cars'] });
      queryClient.invalidateQueries({ queryKey: ['carStats'] });
      setIsFormOpen(false);
      setError(null);
    },
    onError: (error: unknown) => {
      setError(getErrorMessage(error, 'Erro ao criar carro'));
    }
  });

  // Update car mutation
  const updateCarMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: CarUpdateRequest }) => 
      carAPI.updateCar(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cars'] });
      queryClient.invalidateQueries({ queryKey: ['carStats'] });
      setIsFormOpen(false);
      setSelectedCar(undefined);
      setError(null);
    },
    onError: (error: unknown) => {
      setError(getErrorMessage(error, 'Erro ao atualizar carro'));
    }
  });

  // Delete car mutation
  const deleteCarMutation = useMutation({
    mutationFn: (id: string) => carAPI.deleteCar(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cars'] });
      queryClient.invalidateQueries({ queryKey: ['carStats'] });
      setError(null);
    },
    onError: (error: unknown) => {
      setError(getErrorMessage(error, 'Erro ao excluir carro'));
    }
  });

  // Handle form submission
  const handleSubmit = (formData: CarFormData) => {
    const carData = {
      nome: formData.nome,
      unidade: formData.unidade,
      placa: formData.placa || undefined,
      modelo: formData.modelo || undefined,
      cor: formData.cor || undefined,
      status: formData.status,
      observacoes: formData.observacoes || undefined,
    };

    if (selectedCar) {
      updateCarMutation.mutate({ id: selectedCar.id, data: carData });
    } else {
      createCarMutation.mutate(carData);
    }
  };

  // Handle edit
  const handleEdit = (car: Car) => {
    setSelectedCar(car);
    setIsFormOpen(true);
  };

  // Handle delete
  const handleDelete = (car: Car) => {
    if (window.confirm(`Tem certeza que deseja excluir o carro "${car.nome}"?`)) {
      deleteCarMutation.mutate(car.id);
    }
  };

  // Handle form cancel
  const handleCancel = () => {
    setIsFormOpen(false);
    setSelectedCar(undefined);
    setError(null);
  };

  // Handle filters change
  const handleFiltersChange = (newFilters: CarFilter) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: 1 }));
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <TruckIcon className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Gerenciamento de Carros</h1>
            <p className="text-gray-600">Gerencie os veículos utilizados na operação</p>
          </div>
        </div>
        
        <button
          onClick={() => setIsFormOpen(true)}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Novo Carro
        </button>
      </div>

      {/* Stats Cards */}
      {!isLoadingStats && carStats?.success && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg">
                <TruckIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total de Carros</p>
                <p className="text-2xl font-bold text-gray-900">
                  {carStats.stats.total_cars || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg">
                <CheckCircleIcon className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Ativos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {carStats.stats.active_cars || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-12 h-12 bg-yellow-100 rounded-lg">
                <ExclamationTriangleIcon className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Em Manutenção</p>
                <p className="text-2xl font-bold text-gray-900">
                  {carStats.stats.maintenance_cars || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-lg">
                <XCircleIcon className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Inativos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {carStats.stats.inactive_cars || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          <div className="flex items-center">
            <XCircleIcon className="w-5 h-5 mr-2" />
            <span>{error}</span>
            <button 
              onClick={() => setError(null)}
              className="ml-auto text-red-600 hover:text-red-800"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Filters */}
      <CarFilters 
        filters={filters}
        onFiltersChange={handleFiltersChange}
      />

      {/* Cars Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <CarTable
          cars={carsData?.cars || []}
          pagination={carsData?.pagination}
          isLoading={isLoadingCars}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onPageChange={handlePageChange}
        />
      </div>

      {/* Car Form Modal */}
      {isFormOpen && (
        <CarForm
          car={selectedCar}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={createCarMutation.isPending || updateCarMutation.isPending}
        />
      )}
    </div>
  );
};