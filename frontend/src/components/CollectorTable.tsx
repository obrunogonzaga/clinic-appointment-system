import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/20/solid';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import {
    flexRender,
    getCoreRowModel,
    getSortedRowModel,
    useReactTable,
    type ColumnDef,
    type SortingState,
} from '@tanstack/react-table';
import React from 'react';
import type { Collector } from '../types/collector';

interface CollectorTableProps {
  collectors: Collector[];
  isLoading?: boolean;
  onStatusChange?: (id: string, status: string) => void;
  onEdit?: (collector: Collector) => void;
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

export const CollectorTable: React.FC<CollectorTableProps> = ({
  collectors,
  isLoading = false,
  onStatusChange,
  onEdit,
  onDelete
}) => {
  const [sorting, setSorting] = React.useState<SortingState>([]);

  const columns = React.useMemo<ColumnDef<Collector>[]>(
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
        accessorKey: 'cpf',
        header: 'CPF',
        cell: ({ row }) => (
          <div className="text-sm text-gray-900 font-mono">
            {row.original.cpf}
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
        accessorKey: 'registro_profissional',
        header: 'Registro',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.registro_profissional || '-'}
          </div>
        ),
      },
      {
        accessorKey: 'especializacao',
        header: 'Especialização',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.especializacao || '-'}
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
        id: 'actions',
        header: 'Ações',
        cell: ({ row }) => (
          <div className="flex space-x-2">
            <button
              onClick={() => onEdit?.(row.original)}
              className="p-1.5 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
              title="Editar coletora"
            >
              <PencilIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => onDelete?.(row.original.id)}
              className="p-1.5 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
              title="Excluir coletora"
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
    data: collectors,
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
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
            <div className="h-4 bg-gray-300 rounded w-1/4"></div>
          </div>
          <div className="divide-y divide-gray-200">
            {[...Array(5)].map((_, index) => (
              <div key={index} className="px-6 py-4">
                <div className="flex items-center space-x-4">
                  <div className="h-4 bg-gray-300 rounded w-1/4"></div>
                  <div className="h-4 bg-gray-300 rounded w-1/6"></div>
                  <div className="h-4 bg-gray-300 rounded w-1/6"></div>
                  <div className="h-4 bg-gray-300 rounded w-1/6"></div>
                  <div className="h-4 bg-gray-300 rounded w-1/8"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (collectors.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg">
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-2">Nenhuma coletora encontrada</div>
          <div className="text-gray-400 text-sm">
            Tente ajustar os filtros ou cadastre uma nova coletora
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center space-x-1">
                      <span>
                        {flexRender(header.column.columnDef.header, header.getContext())}
                      </span>
                      {{
                        asc: <ChevronUpIcon className="w-4 h-4" />,
                        desc: <ChevronDownIcon className="w-4 h-4" />,
                      }[header.column.getIsSorted() as string] ?? null}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="hover:bg-gray-50 transition-colors">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-6 py-4 whitespace-nowrap">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
