import React from 'react';
import { FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline';
import type { AppointmentFilter } from '../types/appointment';

interface AppointmentFiltersProps {
  filters: AppointmentFilter;
  onFiltersChange: (filters: AppointmentFilter) => void;
  units: string[];
  brands: string[];
  statuses: string[];
  isLoading?: boolean;
}

export const AppointmentFilters: React.FC<AppointmentFiltersProps> = ({
  filters,
  onFiltersChange,
  units,
  brands,
  statuses,
  isLoading = false
}) => {
  const handleFilterChange = (key: keyof AppointmentFilter, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value || undefined,
      page: 1 // Reset page when filters change
    });
  };

  const clearAllFilters = () => {
    onFiltersChange({
      page: 1,
      page_size: filters.page_size || 50
    });
  };

  const hasActiveFilters = Boolean(
    filters.nome_unidade || 
    filters.nome_marca || 
    filters.data || 
    filters.status
  );

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <FunnelIcon className="w-5 h-5 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900">Filtros</h3>
        </div>
        
        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            className="flex items-center space-x-1 text-sm text-red-600 hover:text-red-800 transition-colors"
          >
            <XMarkIcon className="w-4 h-4" />
            <span>Limpar filtros</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {/* Unit Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Unidade
          </label>
          <select
            value={filters.nome_unidade || ''}
            onChange={(e) => handleFilterChange('nome_unidade', e.target.value)}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          >
            <option value="">Todas as unidades</option>
            {units.map((unit) => (
              <option key={unit} value={unit}>
                {unit}
              </option>
            ))}
          </select>
        </div>

        {/* Brand Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Marca
          </label>
          <select
            value={filters.nome_marca || ''}
            onChange={(e) => handleFilterChange('nome_marca', e.target.value)}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          >
            <option value="">Todas as marcas</option>
            {brands.map((brand) => (
              <option key={brand} value={brand}>
                {brand}
              </option>
            ))}
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <select
            value={filters.status || ''}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          >
            <option value="">Todos os status</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        {/* Date Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Data
          </label>
          <input
            type="date"
            value={filters.data || ''}
            onChange={(e) => handleFilterChange('data', e.target.value)}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          />
        </div>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-500">Filtros ativos:</span>
            
            {filters.nome_unidade && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                Unidade: {filters.nome_unidade}
                <button
                  onClick={() => handleFilterChange('nome_unidade', '')}
                  className="ml-1 text-blue-600 hover:text-blue-800"
                >
                  <XMarkIcon className="w-3 h-3" />
                </button>
              </span>
            )}
            
            {filters.nome_marca && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Marca: {filters.nome_marca}
                <button
                  onClick={() => handleFilterChange('nome_marca', '')}
                  className="ml-1 text-green-600 hover:text-green-800"
                >
                  <XMarkIcon className="w-3 h-3" />
                </button>
              </span>
            )}
            
            {filters.status && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                Status: {filters.status}
                <button
                  onClick={() => handleFilterChange('status', '')}
                  className="ml-1 text-yellow-600 hover:text-yellow-800"
                >
                  <XMarkIcon className="w-3 h-3" />
                </button>
              </span>
            )}
            
            {filters.data && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                Data: {new Date(filters.data).toLocaleDateString('pt-BR')}
                <button
                  onClick={() => handleFilterChange('data', '')}
                  className="ml-1 text-purple-600 hover:text-purple-800"
                >
                  <XMarkIcon className="w-3 h-3" />
                </button>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};