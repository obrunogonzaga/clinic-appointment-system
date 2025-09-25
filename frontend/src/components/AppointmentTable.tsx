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
import type { LogisticsPackage } from '../types/logistics-package';
import { TagBadge } from './tags/TagBadge';

interface AppointmentTableProps {
  appointments: AppointmentViewModel[];
  drivers?: ActiveDriver[];
  collectors?: ActiveCollector[];
  logisticsPackages?: LogisticsPackage[];
  isLoading?: boolean;
  onStatusChange?: (id: string, status: string) => void;
  onLogisticsPackageChange?: (
    appointmentId: string,
    logisticsPackageId: string | null,
  ) => void;
  onDelete?: (id: string) => void;
  onSelect?: (appointmentId: string) => void;
  isReadOnly?: boolean;
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
  logisticsPackages = [],
  isLoading = false,
  onStatusChange,
  onLogisticsPackageChange,
  onDelete,
  onSelect,
  isReadOnly = false,
}) => {
  const [sorting, setSorting] = React.useState<SortingState>([
    { id: 'data_agendamento', desc: false },
  ]);

  const resolveAssignedName = (
    assignedId: string | undefined | null,
    people: Array<{ id: string; nome_completo: string }>,
  ): string => {
    if (!assignedId) {
      return 'Não atribuído';
    }

    const match = people.find(person => person.id === assignedId);
    return match?.nome_completo ?? 'Não atribuído';
  };

  const columns = React.useMemo<ColumnDef<AppointmentViewModel>[]>(
    () => [
      {
        accessorKey: 'nome_paciente',
        header: 'Paciente',
        cell: ({ row }) => {
          const { nome_paciente, healthPlanLabel, cpfMasked, cip, telefone } = row.original;
          const hasDetails = Boolean(healthPlanLabel || cpfMasked || cip || telefone);

          return (
            <div className="space-y-2">
              <div className="text-sm font-semibold text-gray-900">{nome_paciente}</div>
              {hasDetails && (
                <div className="space-y-1 text-xs text-gray-500">
                  {healthPlanLabel && (
                    <div className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 font-medium text-blue-700">
                      {healthPlanLabel}
                    </div>
                  )}
                  <div className="flex flex-wrap gap-x-4 gap-y-1">
                    {cpfMasked && <span className="font-mono">CPF: {cpfMasked}</span>}
                    {cip && <span className="font-mono">CIP: {cip}</span>}
                    {telefone && <span>Telefone: {telefone}</span>}
                  </div>
                </div>
              )}
            </div>
          );
        },
      },
      {
        accessorKey: 'data_agendamento',
        header: 'Agendamento',
        sortingFn: (rowA, rowB) => {
          const resolveDateValue = (value?: string | null): number => {
            if (!value) {
              return Number.POSITIVE_INFINITY;
            }
            const timestamp = new Date(value).getTime();
            return Number.isNaN(timestamp)
              ? Number.POSITIVE_INFINITY
              : timestamp;
          };

          const aDateValue = resolveDateValue(rowA.original.data_agendamento);
          const bDateValue = resolveDateValue(rowB.original.data_agendamento);

          if (aDateValue !== bDateValue) {
            return aDateValue - bDateValue;
          }

          const resolveCreatedValue = (value?: string | null): number => {
            if (!value) {
              return 0;
            }
            const timestamp = new Date(value).getTime();
            return Number.isNaN(timestamp) ? 0 : timestamp;
          };

          const aCreated = resolveCreatedValue(rowA.original.created_at);
          const bCreated = resolveCreatedValue(rowB.original.created_at);

          return bCreated - aCreated;
        },
        cell: ({ row }) => {
          const iso = row.original.data_agendamento ?? '';
          const ymd = iso.split('T')[0] || iso;
          const [y, m, d] = ymd.split('-');
          const formatted = y && m && d ? `${d}/${m}/${y}` : '';
          const time = row.original.hora_agendamento ?? '';
          const label = formatted && time
            ? `${formatted} · ${time}`
            : formatted || time || 'Sem data definida';
          const status = row.original.status;
          const colorClass = statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800';

          return (
            <div className="space-y-3">
              <div className="space-y-1">
                <div className="text-sm font-semibold text-gray-900">{label}</div>
                <div className="text-xs text-gray-500">
                  {row.original.cadastrado_por && (
                    <div>Cadastro: {row.original.cadastrado_por}</div>
                  )}
                  {row.original.agendado_por && (
                    <div>Agendado por: {row.original.agendado_por}</div>
                  )}
                </div>
              </div>
              <select
                value={status}
                onChange={(e) => onStatusChange?.(row.original.id, e.target.value)}
                disabled={isReadOnly || !onStatusChange}
                className={`
                  w-full rounded-full border bg-white px-3 py-1 text-xs font-semibold shadow-sm transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1
                  ${colorClass}
                  ${isReadOnly || !onStatusChange ? 'opacity-60 cursor-not-allowed' : ''}
                `}
              >
                {statusOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          );
        },
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
        id: 'team',
        header: 'Equipe',
        enableSorting: false,
        cell: ({ row }) => {
          const appointment = row.original;
          const carroInfo = appointment.carro || '';
          const carroMatch = carroInfo.match(/Carro:\s*([^|]+)/);
          const carro = carroMatch ? carroMatch[1].trim() : carroInfo;
          const driverName = resolveAssignedName(appointment.driver_id, drivers);
          const collectorName = resolveAssignedName(appointment.collector_id, collectors);

          return (
            <div className="space-y-3 text-sm text-gray-600">
              <div className="space-y-1">
                <span className="text-xs font-medium uppercase tracking-wide text-gray-500">Pacote logístico</span>
                {onLogisticsPackageChange && !isReadOnly ? (
                  <select
                    value={appointment.logistics_package_id || ''}
                    onChange={(event) =>
                      onLogisticsPackageChange(
                        appointment.id,
                        event.target.value ? event.target.value : null,
                      )
                    }
                    className="w-full rounded-md border border-gray-300 bg-white px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Sem pacote logístico</option>
                    {logisticsPackages.map(logisticsPackage => (
                      <option key={logisticsPackage.id} value={logisticsPackage.id}>
                        {logisticsPackage.nome}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="rounded-md border border-blue-100 bg-blue-50 px-2 py-1 text-xs text-blue-700">
                    {appointment.logistics_package_name || 'Sem pacote atribuído'}
                  </div>
                )}
              </div>

              <div>
                <span className="text-xs font-medium uppercase tracking-wide text-gray-500">Coletora</span>
                <div className="mt-1 rounded-md border border-gray-200 bg-gray-50 px-2 py-1 text-xs text-gray-700">
                  {collectorName}
                </div>
              </div>

              <div>
                <span className="text-xs font-medium uppercase tracking-wide text-gray-500">Motorista</span>
                <div className="mt-1 rounded-md border border-gray-200 bg-gray-50 px-2 py-1 text-xs text-gray-700">
                  {driverName}
                </div>
              </div>

              {carro && (
                <div className="rounded-md border border-gray-200 bg-gray-50 px-2 py-1 text-xs text-gray-500">
                  Carro: {carro}
                </div>
              )}
            </div>
          );
        },
      },
      {
        id: 'actions',
        header: 'Ações',
        enableSorting: false,
        cell: ({ row }) => (
          <div className="flex space-x-2">
            {!isReadOnly && onDelete && (
              <button
                type="button"
                onClick={(event) => {
                  event.stopPropagation();
                  onDelete?.(row.original.id);
                }}
                className="rounded-full p-1 text-red-600 transition-colors hover:bg-red-50 hover:text-red-700"
                title="Excluir agendamento"
              >
                <TrashIcon className="h-4 w-4" />
              </button>
            )}
          </div>
        ),
      },
    ],
    [
      collectors,
      drivers,
      isReadOnly,
      logisticsPackages,
      onDelete,
      onLogisticsPackageChange,
      onSelect,
      onStatusChange,
    ]
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
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500"
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
            <tr
              key={row.id}
              className={`hover:bg-gray-50 ${onSelect ? 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1' : ''}`}
              onClick={(event) => {
                if (!onSelect) {
                  return;
                }
                const target = event.target as HTMLElement | null;
                if (target && target.closest('button, a, select, input, textarea, label')) {
                  return;
                }
                onSelect(row.original.id);
              }}
              onKeyDown={(event) => {
                if (!onSelect || (event.target as HTMLElement) !== event.currentTarget) {
                  return;
                }
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault();
                  onSelect(row.original.id);
                }
              }}
              tabIndex={onSelect ? 0 : undefined}
            >
              {row.getVisibleCells().map((cell) => (
                <td
                  key={cell.id}
                  className="px-4 py-4 align-top text-sm text-gray-700"
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
