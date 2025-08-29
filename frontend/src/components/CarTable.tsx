import {
    ChevronLeftIcon,
    ChevronRightIcon,
    EyeIcon,
    PencilIcon,
    TrashIcon
} from '@heroicons/react/24/outline';
import React from 'react';
import type { Car, PaginationInfo } from '../types/car';

interface CarTableProps {
  cars: Car[];
  pagination?: PaginationInfo;
  isLoading?: boolean;
  onEdit: (car: Car) => void;
  onDelete: (car: Car) => void;
  onPageChange: (page: number) => void;
}

export const CarTable: React.FC<CarTableProps> = ({
  cars,
  pagination,
  isLoading = false,
  onEdit,
  onDelete,
  onPageChange
}) => {
  const getStatusBadgeClass = (status: string): string => {
    switch (status) {
      case 'Ativo':
        return 'inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800';
      case 'Inativo':
        return 'inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800';
      case 'Manutenção':
        return 'inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800';
      case 'Vendido':
        return 'inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800';
      default:
        return 'inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="p-8 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-sm text-gray-500">Carregando carros...</p>
      </div>
    );
  }

  if (cars.length === 0) {
    return (
      <div className="p-8 text-center">
        <EyeIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhum carro encontrado</h3>
        <p className="mt-1 text-sm text-gray-500">
          Não há carros cadastrados que correspondam aos filtros aplicados.
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Table */}
      <div className="overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nome
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Unidade
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Placa
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Modelo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Criado em
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {cars.map((car) => (
              <tr key={car.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {car.nome}
                  </div>
                  {car.observacoes && (
                    <div className="text-sm text-gray-500 truncate max-w-xs">
                      {car.observacoes}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{car.unidade}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {car.placa || '-'}
                  </div>
                  {car.cor && (
                    <div className="text-sm text-gray-500">{car.cor}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{car.modelo || '-'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={getStatusBadgeClass(car.status)}>
                    {car.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {formatDate(car.created_at)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={() => onEdit(car)}
                      className="text-blue-600 hover:text-blue-800 p-1 rounded hover:bg-blue-50"
                      title="Editar carro"
                    >
                      <PencilIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onDelete(car)}
                      className="text-red-600 hover:text-red-800 p-1 rounded hover:bg-red-50"
                      title="Excluir carro"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && pagination.total_pages > 1 && (
        <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => onPageChange(pagination.page - 1)}
              disabled={!pagination.has_previous}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>
            <button
              onClick={() => onPageChange(pagination.page + 1)}
              disabled={!pagination.has_next}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Próximo
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Mostrando <span className="font-medium">{((pagination.page - 1) * pagination.page_size) + 1}</span> a{' '}
                <span className="font-medium">
                  {Math.min(pagination.page * pagination.page_size, pagination.total_items)}
                </span>{' '}
                de <span className="font-medium">{pagination.total_items}</span> resultados
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  onClick={() => onPageChange(pagination.page - 1)}
                  disabled={!pagination.has_previous}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="sr-only">Anterior</span>
                  <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
                </button>
                
                {/* Page numbers */}
                {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                  const page = i + Math.max(1, pagination.page - 2);
                  if (page > pagination.total_pages) return null;
                  
                  return (
                    <button
                      key={page}
                      onClick={() => onPageChange(page)}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        page === pagination.page
                          ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  );
                })}
                
                <button
                  onClick={() => onPageChange(pagination.page + 1)}
                  disabled={!pagination.has_next}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="sr-only">Próximo</span>
                  <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};