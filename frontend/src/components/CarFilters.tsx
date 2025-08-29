import React, { useState } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import type { CarFilter } from '../types/car';

interface CarFiltersProps {
  filters: CarFilter;
  onFiltersChange: (filters: CarFilter) => void;
  isLoading?: boolean;
}

export const CarFilters: React.FC<CarFiltersProps> = ({
  filters,
  onFiltersChange,
  isLoading = false
}) => {
  const [localFilters, setLocalFilters] = useState<Partial<CarFilter>>({
    nome: filters.nome || '',
    unidade: filters.unidade || '',
    placa: filters.placa || '',
    modelo: filters.modelo || '',
    status: filters.status || '',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    const newFilters = {
      ...localFilters,
      [name]: value
    };
    
    setLocalFilters(newFilters);
    
    // Apply filters with debounce effect
    const filteredValues = Object.fromEntries(
      Object.entries(newFilters).filter(([_, value]) => value !== '')
    );
    
    onFiltersChange(filteredValues);
  };

  const clearFilters = () => {
    const emptyFilters = {
      nome: '',
      unidade: '',
      placa: '',
      modelo: '',
      status: '',
    };
    
    setLocalFilters(emptyFilters);
    onFiltersChange({});
  };

  const hasActiveFilters = Object.values(localFilters).some(value => value !== '');

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 flex items-center">
          <MagnifyingGlassIcon className="w-5 h-5 mr-2" />
          Filtros
        </h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center"
            disabled={isLoading}
          >
            <XMarkIcon className="w-4 h-4 mr-1" />
            Limpar filtros
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Nome */}
        <div>
          <label htmlFor="nome" className="block text-sm font-medium text-gray-700 mb-1">
            Nome do Carro
          </label>
          <input
            type="text"
            id="nome"
            name="nome"
            value={localFilters.nome}
            onChange={handleInputChange}
            placeholder="Ex: CENTER 3 CARRO 1"
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                     disabled:bg-gray-50 disabled:text-gray-500"
          />
        </div>

        {/* Unidade */}
        <div>
          <label htmlFor="unidade" className="block text-sm font-medium text-gray-700 mb-1">
            Unidade
          </label>
          <input
            type="text"
            id="unidade"
            name="unidade"
            value={localFilters.unidade}
            onChange={handleInputChange}
            placeholder="Ex: UND84"
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                     disabled:bg-gray-50 disabled:text-gray-500"
          />
        </div>

        {/* Placa */}
        <div>
          <label htmlFor="placa" className="block text-sm font-medium text-gray-700 mb-1">
            Placa
          </label>
          <input
            type="text"
            id="placa"
            name="placa"
            value={localFilters.placa}
            onChange={handleInputChange}
            placeholder="Ex: ABC-1234"
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                     disabled:bg-gray-50 disabled:text-gray-500"
          />
        </div>

        {/* Modelo */}
        <div>
          <label htmlFor="modelo" className="block text-sm font-medium text-gray-700 mb-1">
            Modelo
          </label>
          <input
            type="text"
            id="modelo"
            name="modelo"
            value={localFilters.modelo}
            onChange={handleInputChange}
            placeholder="Ex: Honda Civic"
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                     disabled:bg-gray-50 disabled:text-gray-500"
          />
        </div>

        {/* Status */}
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="status"
            name="status"
            value={localFilters.status}
            onChange={handleInputChange}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm 
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                     disabled:bg-gray-50 disabled:text-gray-500"
          >
            <option value="">Todos os status</option>
            <option value="Ativo">Ativo</option>
            <option value="Inativo">Inativo</option>
            <option value="Manutenção">Manutenção</option>
            <option value="Vendido">Vendido</option>
          </select>
        </div>
      </div>
    </div>
  );
};