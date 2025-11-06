import React, { useState } from 'react';
import { FunnelIcon, XMarkIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
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
  const [showFilters, setShowFilters] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    const newFilters = {
      ...localFilters,
      [name]: value
    };
    
    setLocalFilters(newFilters);
    
    // Apply filters with debounce effect
    const filteredValues = Object.fromEntries(
      Object.entries(newFilters).filter(([, value]) => value !== '')
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
  const activeFilterCount = Object.values(localFilters).filter(v => v !== '').length;

  return (
    <div className="bg-white dark:bg-slate-950/70 p-4 sm:p-6 rounded-lg shadow-sm border border-gray-200 dark:border-slate-800 mb-6">
      {/* Mobile toggle button */}
      <button
        type="button"
        onClick={() => setShowFilters(!showFilters)}
        className="lg:hidden w-full flex items-center justify-between px-4 py-3 bg-gray-50 dark:bg-slate-800/50 rounded-lg text-sm font-medium text-gray-700 dark:text-slate-200 mb-4"
      >
        <span className="flex items-center gap-2">
          <FunnelIcon className="h-5 w-5" />
          Filtros
          {activeFilterCount > 0 && (
            <span className="bg-indigo-600 text-white text-xs px-2 py-0.5 rounded-full">
              {activeFilterCount}
            </span>
          )}
        </span>
        <ChevronDownIcon className={`h-5 w-5 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
      </button>

      {/* Desktop header */}
      <div className="hidden lg:flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-slate-100 flex items-center">
          <FunnelIcon className="w-5 h-5 mr-2" />
          Filtros
        </h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-gray-600 dark:text-slate-300 hover:text-gray-800 dark:hover:text-slate-100 flex items-center transition"
            disabled={isLoading}
          >
            <XMarkIcon className="w-4 h-4 mr-1" />
            Limpar filtros
          </button>
        )}
      </div>

      <div className={`${showFilters ? 'block' : 'hidden lg:block'}`}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Nome */}
        <div>
          <label htmlFor="nome" className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">
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
            className="w-full px-3 py-2 border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-100 placeholder:text-gray-400 dark:placeholder:text-slate-400 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 disabled:opacity-50 transition-colors"
          />
        </div>

        {/* Unidade */}
        <div>
          <label htmlFor="unidade" className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">
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
            className="w-full px-3 py-2 border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-100 placeholder:text-gray-400 dark:placeholder:text-slate-400 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 disabled:opacity-50 transition-colors"
          />
        </div>

        {/* Placa */}
        <div>
          <label htmlFor="placa" className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">
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
            className="w-full px-3 py-2 border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-100 placeholder:text-gray-400 dark:placeholder:text-slate-400 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 disabled:opacity-50 transition-colors"
          />
        </div>

        {/* Modelo */}
        <div>
          <label htmlFor="modelo" className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">
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
            className="w-full px-3 py-2 border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-100 placeholder:text-gray-400 dark:placeholder:text-slate-400 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 disabled:opacity-50 transition-colors"
          />
        </div>

        {/* Status */}
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">
            Status
          </label>
          <select
            id="status"
            name="status"
            value={localFilters.status}
            onChange={handleInputChange}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-100 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 disabled:opacity-50 transition-colors"
          >
            <option value="">Todos os status</option>
            <option value="Ativo">Ativo</option>
            <option value="Inativo">Inativo</option>
            <option value="Manutenção">Manutenção</option>
            <option value="Vendido">Vendido</option>
          </select>
        </div>
      </div>

        {/* Mobile clear button */}
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="lg:hidden w-full mt-3 flex items-center justify-center px-4 py-2 text-sm text-gray-600 dark:text-slate-300 hover:text-gray-800 dark:hover:text-slate-100 border border-gray-300 dark:border-slate-700 rounded-md transition"
            disabled={isLoading}
          >
            <XMarkIcon className="w-4 h-4 mr-1" />
            Limpar filtros
          </button>
        )}

        {/* Active filters badges */}
        {hasActiveFilters && (
          <div className="mt-4 flex flex-wrap gap-2">
            {Object.entries(localFilters)
              .filter(([, value]) => value !== '')
              .map(([key, value]) => (
                <span
                  key={key}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-500/20 text-blue-800 dark:text-blue-200"
                >
                  {key === 'nome' && 'Nome: '}
                  {key === 'unidade' && 'Unidade: '}
                  {key === 'placa' && 'Placa: '}
                  {key === 'modelo' && 'Modelo: '}
                  {key === 'status' && 'Status: '}
                  {value}
                </span>
              ))}
          </div>
        )}
      </div>
    </div>
  );
};