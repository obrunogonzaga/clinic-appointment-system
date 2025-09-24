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
import type { AppointmentViewModel } from '../types/appointment.ts';
import type { ActiveCollector } from '../types/collector.ts';
import type { ActiveDriver } from '../types/driver.ts';
import { TagBadge } from './tags/TagBadge';

interface AppointmentTableProps {
  appointments: AppointmentViewModel[];
  drivers?: ActiveDriver[];
  collectors?: ActiveCollector[];
  isLoading?: boolean;
  onStatusChange?: (id: string, status: string) => void;
  onDriverChange?: (appointmentId: string, driverId: string) => void;
  onCollectorChange?: (appointmentId: string, collectorId: string) => void;
  onDelete?: (id: string) => void;
}

const statusColors = {
  'Pendente': 'bg-yellow-50 text-yellow-700 border-yellow-200',
  'Autorização': 'bg-indigo-50 text-indigo-700 border-indigo-200',
  'Cadastrar': 'bg-blue-50 text-blue-700 border-blue-200',
  'Agendado': 'bg-sky-50 text-sky-700 border-sky-200',
  'Confirmado': 'bg-green-50 text-green-700 border-green-200',
  'Coletado': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'Alterar': 'bg-purple-50 text-purple-700 border-purple-200',
  'Cancelado': 'bg-red-50 text-red-700 border-red-200',
  'Recoleta': 'bg-orange-50 text-orange-700 border-orange-200',
};

const statusOptions = [
  'Pendente',
  'Autorização',
  'Cadastrar',
  'Agendado',
  'Confirmado',
  'Coletado',
  'Alterar',
  'Cancelado',
  'Recoleta'
];

export const AppointmentTable: React.FC<AppointmentTableProps> = ({
  appointments,
  drivers = [],
  collectors = [],
  isLoading = false,
  onStatusChange,
  onDriverChange,
  onCollectorChange,
  onDelete
}) => {
  const [sorting, setSorting] = React.useState<SortingState>([]);

  const columns = React.useMemo<ColumnDef<AppointmentViewModel>[]>(
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
        id: 'cpfMasked',
        header: 'CPF',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600 font-mono">
            {row.original.cpfMasked || '-'}
          </div>
        ),
      },
      {
        accessorKey: 'cip',
        header: 'CIP',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600 font-mono">
            {row.original.cip || '-'}
          </div>
        ),
      },
      {
        id: 'healthPlanLabel',
        header: 'Plano',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.healthPlanLabel}
          </div>
        ),
      },
      {
        accessorKey: 'data_agendamento',
        header: 'Data',
        cell: ({ row }) => {
          const iso = row.original.data_agendamento ?? '';
          const ymd = iso.split('T')[0] || iso;
          const [y, m, d] = ymd.split('-');
          const formatted = y && m && d ? `${d}/${m}/${y}` : '';
          const time = row.original.hora_agendamento;
          const label = formatted && time ? `${formatted} · ${time}` : formatted || time || '-';
          return (
            <div className="text-sm font-semibold text-gray-900">
              {label}
            </div>
          );
        },
      },
      {
        id: 'unitBrand',
        header: 'Unidade / Marca',
        cell: ({ row }) => {
          const unit = row.original.nome_unidade;
          const brand = row.original.nome_marca;
          const label = unit && brand ? `${unit} · ${brand}` : unit || brand || '-';
          return (
            <div className="text-sm font-medium text-gray-700">
              {label}
            </div>
          );
        },
      },
      {
        id: 'address',
        header: 'Endereço',
        cell: ({ row }) => {
          const normalized = row.original.endereco_normalizado;
          const street = normalized?.rua || row.original.endereco_coleta || row.original.nome_unidade;
          const number = normalized?.numero ? `, ${normalized.numero}` : '';
          const city = normalized?.cidade ? ` - ${normalized.cidade}` : '';
          return (
            <div className="text-sm text-gray-600">
              {street ? `${street}${number}${city}` : '-'}
            </div>
          );
        },
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
                rounded-full border bg-white px-3 py-1 text-xs font-semibold shadow-sm transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1
                ${colorClass}
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
        accessorKey: 'cadastrado_por',
        header: 'Cadastrado por',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.cadastrado_por || '-'}
          </div>
        ),
      },
      {
        accessorKey: 'agendado_por',
        header: 'Agendado por',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">
            {row.original.agendado_por || '-'}
          </div>
        ),
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
        id: 'tags',
        header: 'Tags',
        cell: ({ row }) => {
          const tags = row.original.tags ?? [];
          if (tags.length === 0) {
            return <span className="text-xs text-gray-400">-</span>;
          }
          return (
            <div className="flex flex-wrap gap-1.5">
              {tags.map((tag) => (
                <TagBadge key={tag.id} name={tag.name} color={tag.color} size="sm" />
              ))}
            </div>
          );
        },
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
        accessorKey: 'collector_id',
        header: 'Coletora',
        cell: ({ row }) => {
          const appointment = row.original;
          
          return (
            <select
              value={appointment.collector_id || ''}
              onChange={(e) => onCollectorChange?.(appointment.id, e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Selecionar coletora</option>
              {collectors.map((collector) => (
                <option key={collector.id} value={collector.id}>
                  {collector.nome_completo}
                </option>
              ))}
            </select>
          );
        },
      },
      {
        id: 'carro',
        header: 'Carro',
        cell: ({ row }) => {
          const carroInfo = row.original.carro || '';
          const carroMatch = carroInfo.match(/Carro:\s*([^|]+)/);
          const carro = carroMatch ? carroMatch[1].trim() : carroInfo;

          return (
            <div className="text-sm text-gray-600 font-mono">
              {carro || '-'}
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
    [onStatusChange, onDriverChange, onCollectorChange, onDelete, drivers, collectors]
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
    <div className="overflow-x-auto rounded-2xl border border-gray-100 bg-white shadow-sm">
      <table className="min-w-full overflow-hidden rounded-2xl">
        <thead className="bg-gray-50">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500"
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
        <tbody className="divide-y divide-gray-100">
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="hover:bg-gray-50">
              {row.getVisibleCells().map((cell) => (
                <td
                  key={cell.id}
                  className="px-6 py-4 text-sm text-gray-700"
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
