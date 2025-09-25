import React, { useEffect, useState } from 'react';
import { FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline';
import type { AppointmentFilter } from '../types/appointment';
import { SearchInput } from './ui/SearchInput';
import type { DateShortcut } from '../utils/appointmentViewModel';

interface AppointmentFiltersProps {
  filters: AppointmentFilter;
  onFiltersChange: (filters: AppointmentFilter) => void;
  units: string[];
  brands: string[];
  statuses: string[];
  searchTerm: string;
  onSearchChange: (value: string) => void;
  dateShortcut: DateShortcut | null;
  onDateShortcutChange: (shortcut: DateShortcut | null) => void;
  isLoading?: boolean;
}

const dateShortcutOptions: Array<{ label: string; value: DateShortcut }> = [
  { label: 'Hoje', value: 'today' },
  { label: 'Amanhã', value: 'tomorrow' },
  { label: 'Esta semana', value: 'thisWeek' },
  { label: 'Próxima semana', value: 'nextWeek' },
];

export const AppointmentFilters: React.FC<AppointmentFiltersProps> = ({
  filters,
  onFiltersChange,
  units,
  brands,
  statuses,
  searchTerm,
  onSearchChange,
  dateShortcut,
  onDateShortcutChange,
  isLoading = false,
}) => {
  const [localSearch, setLocalSearch] = useState(searchTerm);

  useEffect(() => {
    setLocalSearch(searchTerm);
  }, [searchTerm]);

  const handleFilterChange = (key: keyof AppointmentFilter, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value || undefined,
      page: 1,
    });
  };

  const resetFilters = () => {
    onFiltersChange({
      page: 1,
      page_size: filters.page_size || 50,
      scope: filters.scope,
    });
    setLocalSearch('');
    onSearchChange('');
    onDateShortcutChange(null);
  };

  const hasActiveFilters = Boolean(
    filters.nome_unidade ||
    filters.nome_marca ||
    filters.data ||
    filters.status ||
    searchTerm ||
    dateShortcut
  );

  const handleDateShortcut = (shortcut: DateShortcut) => {
    if (dateShortcut === shortcut) {
      onDateShortcutChange(null);
      if (shortcut === 'today' || shortcut === 'tomorrow') {
        handleFilterChange('data', '');
      }
      return;
    }

    onDateShortcutChange(shortcut);

    if (shortcut === 'today' || shortcut === 'tomorrow') {
      const targetDate = new Date();
      if (shortcut === 'tomorrow') {
        targetDate.setDate(targetDate.getDate() + 1);
      }
      const formatted = targetDate.toISOString().split('T')[0];
      handleFilterChange('data', formatted);
      return;
    }

    // Remove data filter for weekly ranges (handled client-side)
    if (filters.data) {
      handleFilterChange('data', '');
    }
  };

  const handleDateInputChange = (value: string) => {
    onDateShortcutChange(null);
    handleFilterChange('data', value);
  };

  const handleApply = () => {
    onSearchChange(localSearch);
  };

  const filterBadgeClass = hasActiveFilters
    ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-200'
    : 'bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-200';

  return (
    <div className="rounded-2xl border border-gray-100 dark:border-slate-800 bg-white dark:bg-slate-950/70 p-6 shadow-sm transition-colors">
      <div className="flex flex-wrap items-center gap-3">
        <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${filterBadgeClass}`}>
          <FunnelIcon className="h-4 w-4" />
          Filtros
        </div>
        <div className="ml-auto flex items-center gap-2">
          <button
            type="button"
            onClick={resetFilters}
            className="inline-flex items-center rounded-full border border-gray-200 dark:border-slate-700 px-4 py-2 text-sm font-medium text-gray-600 dark:text-slate-300 transition hover:border-gray-300 hover:text-gray-800 dark:hover:border-slate-600 dark:hover:text-slate-100"
          >
            <XMarkIcon className="mr-1 h-4 w-4" />
            Limpar
          </button>
          <button
            type="button"
            onClick={handleApply}
            className="inline-flex items-center rounded-full bg-gray-900 dark:bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-gray-800 dark:hover:bg-indigo-500"
          >
            Aplicar
          </button>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-12">
        <div className="lg:col-span-2">
          <label htmlFor="filter-unit" className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-300">
            Unidade
          </label>
          <select
            id="filter-unit"
            value={filters.nome_unidade || ''}
            onChange={(event) => handleFilterChange('nome_unidade', event.target.value)}
            disabled={isLoading}
            className="mt-2 w-full rounded-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-sm text-gray-700 dark:text-slate-100 placeholder:text-gray-400 dark:placeholder:text-slate-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:focus:ring-indigo-400 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
          >
            <option value="">Todas as unidades</option>
            {units.map((unit) => (
              <option key={unit} value={unit}>
                {unit}
              </option>
            ))}
          </select>
        </div>

        <div className="lg:col-span-2">
          <label htmlFor="filter-brand" className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-300">
            Marca
          </label>
          <select
            id="filter-brand"
            value={filters.nome_marca || ''}
            onChange={(event) => handleFilterChange('nome_marca', event.target.value)}
            disabled={isLoading}
            className="mt-2 w-full rounded-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-sm text-gray-700 dark:text-slate-100 placeholder:text-gray-400 dark:placeholder:text-slate-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:focus:ring-indigo-400 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
          >
            <option value="">Todas as marcas</option>
            {brands.map((brand) => (
              <option key={brand} value={brand}>
                {brand}
              </option>
            ))}
          </select>
        </div>

        <div className="lg:col-span-2">
          <label htmlFor="filter-status" className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-300">
            Status
          </label>
          <select
            id="filter-status"
            value={filters.status || ''}
            onChange={(event) => handleFilterChange('status', event.target.value)}
            disabled={isLoading}
            className="mt-2 w-full rounded-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-sm text-gray-700 dark:text-slate-100 placeholder:text-gray-400 dark:placeholder:text-slate-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:focus:ring-indigo-400 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
          >
            <option value="">Todos os status</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        <div className="lg:col-span-2">
          <label htmlFor="filter-date" className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-300">
            Data
          </label>
          <input
            id="filter-date"
            type="date"
            value={filters.data || ''}
            onChange={(event) => handleDateInputChange(event.target.value)}
            disabled={isLoading}
            className="mt-2 w-full rounded-full border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-sm text-gray-700 dark:text-slate-100 placeholder:text-gray-400 dark:placeholder:text-slate-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:focus:ring-indigo-400 disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
          />
        </div>

        <div className="lg:col-span-4">
          <label className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-300">
            Buscar por nome ou CPF
          </label>
          <div className="mt-2">
            <SearchInput
              value={localSearch}
              onChange={(value) => setLocalSearch(value)}
              placeholder="Buscar por nome/CPF"
              className="rounded-full"
              inputClassName="rounded-full border border-gray-200 dark:border-slate-700"
              debounceMs={0}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  event.preventDefault();
                  handleApply();
                }
              }}
            />
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className="text-sm font-semibold text-gray-600 dark:text-slate-300">Atalhos:</span>
        {dateShortcutOptions.map(({ label, value }) => {
          const isActive = dateShortcut === value;
          return (
            <button
              key={value}
              type="button"
              onClick={() => handleDateShortcut(value)}
              className={`rounded-full px-4 py-1 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-slate-200 hover:bg-gray-200 dark:hover:bg-slate-700'
              }`}
              aria-pressed={isActive}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
};
