import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/20/solid';
import { TrashIcon } from '@heroicons/react/24/outline';
import {
    flexRender,
    getCoreRowModel,
    getSortedRowModel,
    useReactTable,
    type ColumnDef,
    type SortingState,
} from '@tanstack/react-table';
import React from 'react';
import type { Appointment } from '../types/appointment.ts';
import type { ActiveDriver } from '../types/driver.ts';

interface AppointmentTableProps {
  appointments: Appointment[];
  drivers?: ActiveDriver[];
  isLoading?: boolean;
  onStatusChange?: (id: string, status: string) => void;
  onDriverChange?: (appointmentId: string, driverId: string) => void;
  onDelete?: (id: string) => void;
}

const statusColors = {
  'Confirmado': 'bg-green-50 text-green-700 border-green-200',
  'Cancelado': 'bg-red-50 text-red-700 border-red-200',
  'Reagendado': 'bg-yellow-50 text-yellow-700 border-yellow-200',
  'Concluído': 'bg-blue-50 text-blue-700 border-blue-200',
  'Não Compareceu': 'bg-gray-50 text-gray-700 border-gray-200',
};

const statusOptions = [
  'Confirmado',
  'Cancelado', 
  'Reagendado',
  'Concluído',
  'Não Compareceu'
];

export const AppointmentTable: React.FC<AppointmentTableProps> = ({
  appointments,
  drivers = [],
  isLoading = false,
  onStatusChange,
  onDriverChange,
  onDelete
}) => {
  const [sorting, setSorting] = React.useState<SortingState>([]);

  const columns = React.useMemo<ColumnDef<Appointment>[]>(
    () => [
      {
        accessorKey: 'nome_paciente',
        header: 'Paciente',
        cell: ({ row }) => (
          <div className="font-medium text-gray-900">
            {row.original.nome_paciente}
          </div>
        ),
      },
      {
        accessorKey: 'nome_unidade',
        header: 'Unidade',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.nome_unidade}
          </div>
        ),
      },
      {
        id: 'carro',
        header: 'Carro',
        cell: ({ row }) => {
          // Extrai informação do carro das observações
          const obs = row.original.observacoes || '';
          const carroMatch = obs.match(/Carro:\s*([^|]+)/);
          const carro = carroMatch ? carroMatch[1].trim() : '';
          
          return (
            <div className="text-sm text-gray-600 font-mono">
              {carro || '-'}
            </div>
          );
        },
      },
      {
        accessorKey: 'nome_marca',
        header: 'Marca',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.nome_marca}
          </div>
        ),
      },
      {
        accessorKey: 'data_agendamento',
        header: 'Data',
        cell: ({ row }) => {
          const iso = row.original.data_agendamento ?? '';
          const ymd = iso.split('T')[0] || iso; // "YYYY-MM-DD"
          const [y, m, d] = ymd.split('-');
          const formatted = y && m && d ? `${d}/${m}/${y}` : '';
          return (
            <div className="text-sm text-gray-900">
              {formatted || '-'}
            </div>
          );
        },
      },
      {
        accessorKey: 'hora_agendamento',
        header: 'Hora',
        cell: ({ row }) => (
          <div className="text-sm text-gray-900">
            {row.original.hora_agendamento}
          </div>
        ),
      },
      {
        accessorKey: 'tipo_consulta',
        header: 'Tipo',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.tipo_consulta || '-'}
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
        accessorKey: 'telefone',
        header: 'Telefone',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.telefone || '-'}
          </div>
        ),
      },
      {
        accessorKey: 'driver_id',
        header: 'Motorista',
        cell: ({ row }) => {
          const appointment = row.original;
          
          return (
            <select
              value={appointment.driver_id || ''}
              onChange={(e) => onDriverChange?.(appointment.id, e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Selecionar motorista</option>
              {drivers.map((driver) => (
                <option key={driver.id} value={driver.id}>
                  {driver.nome_completo}
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
              onClick={() => onDelete?.(row.original.id)}
              className="p-1 text-red-600 hover:text-red-800 transition-colors"
              title="Excluir agendamento"
            >
              <TrashIcon className="w-4 h-4" />
            </button>
          </div>
        ),
      },
    ],
    [onStatusChange, onDriverChange, onDelete, drivers]
  );

  const table = useReactTable({
    data: appointments,
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

  if (appointments.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">
          Nenhum agendamento encontrado
        </div>
        <div className="text-gray-400 text-sm mt-2">
          Faça upload de um arquivo Excel ou ajuste os filtros
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