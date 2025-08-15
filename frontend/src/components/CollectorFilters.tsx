import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import React, { useState } from 'react';
import type { CollectorFilter } from '../types/collector';

interface CollectorFiltersProps {
  onFilterChange: (filters: CollectorFilter) => void;
  isLoading?: boolean;
}

export const CollectorFilters: React.FC<CollectorFiltersProps> = ({
  onFilterChange,
  isLoading = false
}) => {
  const [filters, setFilters] = useState<CollectorFilter>({
    nome_completo: '',
    cpf: '',
    telefone: '',
    email: '',
    status: '',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    const newFilters = {
      ...filters,
      [name]: value
    };
    
    setFilters(newFilters);
    
    // Apply filters with debounce effect
    const filteredValues = Object.fromEntries(
      Object.entries(newFilters).filter(([_, value]) => value !== '')
    );
    
    onFilterChange(filteredValues);
  };

  const clearFilters = () => {
    const emptyFilters = {
      nome_completo: '',
      cpf: '',
      telefone: '',
      email: '',
      status: '',
    };
    
    setFilters(emptyFilters);
    onFilterChange({});
  };

  const hasActiveFilters = Object.values(filters).some(value => value !== '');

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
          >
            <XMarkIcon className="w-4 h-4 mr-1" />
            Limpar filtros
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Nome Completo */}
        <div>
          <label htmlFor="nome_completo" className="block text-sm font-medium text-gray-700 mb-1">
            Nome Completo
          </label>
          <input
            type="text"
            id="nome_completo"
            name="nome_completo"
            value={filters.nome_completo}
            onChange={handleInputChange}
            placeholder="Filtrar por nome..."
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
        </div>

        {/* CPF */}
        <div>
          <label htmlFor="cpf" className="block text-sm font-medium text-gray-700 mb-1">
            CPF
          </label>
          <input
            type="text"
            id="cpf"
            name="cpf"
            value={filters.cpf}
            onChange={handleInputChange}
            placeholder="Filtrar por CPF..."
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
        </div>

        {/* Telefone */}
        <div>
          <label htmlFor="telefone" className="block text-sm font-medium text-gray-700 mb-1">
            Telefone
          </label>
          <input
            type="text"
            id="telefone"
            name="telefone"
            value={filters.telefone}
            onChange={handleInputChange}
            placeholder="Filtrar por telefone..."
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
        </div>

        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={filters.email}
            onChange={handleInputChange}
            placeholder="Filtrar por email..."
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
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
            value={filters.status}
            onChange={handleInputChange}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <option value="">Todos os status</option>
            <option value="Ativo">Ativo</option>
            <option value="Inativo">Inativo</option>
            <option value="Suspenso">Suspenso</option>
            <option value="Férias">Férias</option>
          </select>
        </div>
      </div>

      {hasActiveFilters && (
        <div className="mt-4 flex flex-wrap gap-2">
          {Object.entries(filters)
            .filter(([_, value]) => value !== '')
            .map(([key, value]) => (
              <span
                key={key}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {key === 'nome_completo' && 'Nome: '}
                {key === 'cpf' && 'CPF: '}
                {key === 'telefone' && 'Telefone: '}
                {key === 'email' && 'Email: '}
                {key === 'status' && 'Status: '}
                {value}
              </span>
            ))}
        </div>
      )}
    </div>
  );
};
