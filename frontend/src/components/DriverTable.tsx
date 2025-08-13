import React from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  type ColumnDef,
  type SortingState,
  flexRender,
} from '@tanstack/react-table';
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/20/solid';
import { TrashIcon, PencilIcon } from '@heroicons/react/24/outline';
import type { Driver } from '../types/driver';

interface DriverTableProps {
  drivers: Driver[];
  isLoading?: boolean;
  onStatusChange?: (id: string, status: string) => void;
  onEdit?: (driver: Driver) => void;
  onDelete?: (id: string) => void;
}

const statusColors = {
  'Ativo': 'bg-green-50 text-green-700 border-green-200',
  'Inativo': 'bg-red-50 text-red-700 border-red-200',
  'Suspenso': 'bg-yellow-50 text-yellow-700 border-yellow-200',
  'Férias': 'bg-blue-50 text-blue-700 border-blue-200',
};

const statusOptions = [
  'Ativo',
  'Inativo',
  'Suspenso',
  'Férias'
];

export const DriverTable: React.FC<DriverTableProps> = ({
  drivers,
  isLoading = false,
  onStatusChange,
  onEdit,
  onDelete
}) => {
  const [sorting, setSorting] = React.useState<SortingState>([]);

  const columns = React.useMemo<ColumnDef<Driver>[]>(
    () => [
      {
        accessorKey: 'nome_completo',
        header: 'Nome Completo',
        cell: ({ row }) => (
          <div className="font-medium text-gray-900">
            {row.original.nome_completo}
          </div>
        ),
      },
      {
        accessorKey: 'cnh',
        header: 'CNH',
        cell: ({ row }) => (
          <div className="text-sm text-gray-900 font-mono">
            {row.original.cnh}
          </div>
        ),
      },
      {
        accessorKey: 'telefone',
        header: 'Telefone',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.telefone}
          </div>
        ),
      },
      {
        accessorKey: 'email',
        header: 'Email',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.email || '-'}
          </div>
        ),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => {
          const status = row.original.status;
          const colorClass = statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800';
          
          return (
            <select
              value={status}
              onChange={(e) => onStatusChange?.(row.original.id, e.target.value)}
              className={`
                px-3 py-1.5 rounded-lg text-xs font-medium border cursor-pointer transition-all
                ${colorClass}
                hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-500
              `}
            >
              {statusOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          );
        },
      },
      {
        accessorKey: 'created_at',
        header: 'Cadastrado em',
        cell: ({ row }) => {
          const date = new Date(row.original.created_at);
          return (
            <div className="text-sm text-gray-600">
              {date.toLocaleDateString('pt-BR')}
            </div>
          );
        },
      },
      {
        id: 'actions',
        header: 'Ações',
        cell: ({ row }) => (
          <div className="flex space-x-2">
            <button
              onClick={() => onEdit?.(row.original)}
              className="p-1 text-blue-600 hover:text-blue-800 transition-colors"
              title="Editar motorista"
            >
              <PencilIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => onDelete?.(row.original.id)}
              className="p-1 text-red-600 hover:text-red-800 transition-colors"
              title="Excluir motorista"
            >
              <TrashIcon className="w-4 h-4" />
            </button>
          </div>
        ),
      },
    ],
    [onStatusChange, onEdit, onDelete]
  );

  const table = useReactTable({
    data: drivers,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: {
      sorting,
    },
    onSortingChange: setSorting,
  });

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded mb-4"></div>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-12 bg-gray-100 rounded mb-2"></div>
        ))}
      </div>
    );
  }

  if (drivers.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">
          Nenhum motorista encontrado
        </div>
        <div className="text-gray-400 text-sm mt-2">
          Cadastre um novo motorista ou ajuste os filtros
        </div>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {header.isPlaceholder ? null : (
                    <div
                      className={`
                        ${header.column.getCanSort() ? 'cursor-pointer select-none flex items-center' : ''}
                      `}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                      {header.column.getCanSort() && (
                        <span className="ml-1">
                          {header.column.getIsSorted() === 'desc' ? (
                            <ChevronDownIcon className="w-4 h-4" />
                          ) : header.column.getIsSorted() === 'asc' ? (
                            <ChevronUpIcon className="w-4 h-4" />
                          ) : (
                            <ChevronUpIcon className="w-4 h-4 opacity-50" />
                          )}
                        </span>
                      )}
                    </div>
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="hover:bg-gray-50">
              {row.getVisibleCells().map((cell) => (
                <td
                  key={cell.id}
                  className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                >
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};