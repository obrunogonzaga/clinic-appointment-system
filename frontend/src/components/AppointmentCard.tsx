import {
    BuildingOfficeIcon,
    CalendarIcon,
    ClockIcon,
    CreditCardIcon,
    IdentificationIcon,
    PhoneIcon,
    TrashIcon,
    TruckIcon,
    UserIcon,
} from '@heroicons/react/24/outline';
import React from 'react';
import type { AppointmentViewModel } from '../types/appointment';
import type { ActiveCollector } from '../types/collector';
import type { ActiveDriver } from '../types/driver';
import type { LogisticsPackage } from '../types/logistics-package';
import { formatDate } from '../utils/dateUtils';
import { getStatusBadgeClass } from '../utils/statusColors';
import { TagBadge } from './tags/TagBadge';

interface AppointmentCardProps {
  appointment: AppointmentViewModel;
  drivers: ActiveDriver[];
  collectors?: ActiveCollector[];
  onStatusChange: (id: string, status: string) => void;
  logisticsPackages?: LogisticsPackage[];
  onLogisticsPackageChange?: (
    appointmentId: string,
    logisticsPackageId: string | null,
  ) => void;
  onDelete: (id: string) => void;
  compact?: boolean;
  onSelect?: (id: string) => void;
}

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

export const AppointmentCard: React.FC<AppointmentCardProps> = ({
  appointment,
  drivers,
  collectors = [],
  logisticsPackages = [],
  onStatusChange,
  onLogisticsPackageChange,
  onDelete,
  compact = false,
  onSelect,
}) => {
  const getCarInfo = (): string => {
    if (appointment.carro) {
      const carroRegex = /Carro:\s*([^|]+)/;
      const carroMatch = carroRegex.exec(appointment.carro);
      return carroMatch ? carroMatch[1].trim() : appointment.carro;
    }

    return '-';
  };

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

  const driverName = resolveAssignedName(appointment.driver_id, drivers);
  const collectorName = resolveAssignedName(appointment.collector_id, collectors);

  const handleDelete = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    if (window.confirm('Tem certeza que deseja excluir este agendamento?')) {
      onDelete(appointment.id);
    }
  };

  const handleCardClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (!onSelect) {
      return;
    }

    const target = event.target as HTMLElement | null;
    if (target && target.closest('button, a, select, input, textarea, label')) {
      return;
    }

    onSelect(appointment.id);
  };

  const handleCardKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (!onSelect || (event.target as HTMLElement) !== event.currentTarget) {
      return;
    }

    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onSelect(appointment.id);
    }
  };

  const addressLabel = (() => {
    const street = appointment.endereco_normalizado?.rua || appointment.endereco_coleta;
    const number = appointment.endereco_normalizado?.numero;

    if (street) {
      return number ? `${street}, ${number}` : street;
    }

    return appointment.nome_unidade;
  })();

  const detailLabelClass = 'text-[11px] font-semibold uppercase tracking-wide text-gray-400';
  const detailValueClass = `${compact ? 'text-xs' : 'text-sm'} text-gray-700`;

  return (
    <div
      className={`
      rounded-2xl border border-gray-100 bg-white shadow-sm transition-all duration-200
      hover:shadow-md hover:border-gray-200
      ${onSelect ? 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2' : ''}
      ${compact ? 'p-3' : 'p-5'}
    `}
      onClick={handleCardClick}
      onKeyDown={handleCardKeyDown}
      role={onSelect ? 'button' : undefined}
      tabIndex={onSelect ? 0 : undefined}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center min-w-0 flex-1">
          <UserIcon className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0" />
          <h3 className={`
            font-medium text-gray-900 truncate
            ${compact ? 'text-sm' : 'text-base'}
          `}>
            {appointment.nome_paciente}
          </h3>
        </div>
        
        <select
          value={appointment.status}
          onChange={(e) => onStatusChange(appointment.id, e.target.value)}
          className={`
            ml-3 cursor-pointer transition-all flex-shrink-0
            focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-500
            ${getStatusBadgeClass(appointment.status)}
          `}
        >
          {statusOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>

      {appointment.tags && appointment.tags.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {appointment.tags.map((tag) => (
            <TagBadge key={tag.id} name={tag.name} color={tag.color} size="sm" />
          ))}
        </div>
      )}

      {/* Body */}
      <div className={`mt-4 grid grid-cols-1 gap-4 ${compact ? '' : 'md:grid-cols-2'}`}>
        <div className="space-y-4">
          <div>
            <p className={detailLabelClass}>Pacote logístico</p>
            <p className={detailValueClass}>
              {appointment.logistics_package_name || 'Sem pacote atribuído'}
            </p>
          </div>
          <div>
            <p className={detailLabelClass}>Data e horário</p>
            <div className={`mt-1 flex flex-wrap items-center gap-2 ${detailValueClass}`}>
              <span className="inline-flex items-center gap-1 rounded-full bg-gray-50 px-2 py-1 font-medium text-gray-600">
                <CalendarIcon className="w-3 h-3" />
                {formatDate(appointment.data_agendamento ?? '')}
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-gray-50 px-2 py-1 font-medium text-gray-600">
                <ClockIcon className="w-3 h-3" />
                {appointment.hora_agendamento ?? 'Sem hora definida'}
              </span>
            </div>
          </div>

          <div>
            <p className={detailLabelClass}>Local</p>
            <div className={`mt-1 flex items-start gap-2 ${detailValueClass}`}>
              <BuildingOfficeIcon className="w-4 h-4 text-gray-400" />
              <span className="leading-snug">{addressLabel}</span>
            </div>
          </div>

          <div>
            <p className={detailLabelClass}>Veículo</p>
            <div className={`mt-1 flex items-start gap-2 ${detailValueClass}`}>
              <TruckIcon className="w-4 h-4 text-gray-400" />
              <span className="leading-snug">{getCarInfo()}</span>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {appointment.cip && (
            <div>
              <p className={detailLabelClass}>CIP</p>
              <div className={`mt-1 flex items-center gap-2 ${detailValueClass}`}>
                <IdentificationIcon className="w-4 h-4 text-gray-400" />
                <span className="leading-snug">{appointment.cip}</span>
              </div>
            </div>
          )}

          {appointment.cpfMasked && (
            <div>
              <p className={detailLabelClass}>CPF</p>
              <div className={`mt-1 flex items-center gap-2 ${detailValueClass}`}>
                <IdentificationIcon className="w-4 h-4 text-gray-400" />
                <span className="leading-snug">{appointment.cpfMasked}</span>
              </div>
            </div>
          )}

          <div>
            <p className={detailLabelClass}>Plano de saúde</p>
            <div className={`mt-1 flex items-center gap-2 ${detailValueClass}`}>
              <CreditCardIcon className="w-4 h-4 text-gray-400" />
              <span className="leading-snug">{appointment.healthPlanLabel}</span>
            </div>
          </div>

          {(() => {
            const rgFormatted = appointment.documento_normalizado?.rg_formatted;
            if (!rgFormatted) {
              return null;
            }

            return (
              <div>
                <p className={detailLabelClass}>RG</p>
                <div className={`mt-1 flex items-center gap-2 ${detailValueClass}`}>
                  <IdentificationIcon className="w-4 h-4 text-gray-400" />
                  <span className="leading-snug">{rgFormatted}</span>
                </div>
              </div>
            );
          })()}

          {appointment.telefone && (
            <div>
              <p className={detailLabelClass}>Contato</p>
              <div className={`mt-1 flex items-center gap-2 ${detailValueClass}`}>
                <PhoneIcon className="w-4 h-4 text-gray-400" />
                <span className="leading-snug">{appointment.telefone}</span>
              </div>
            </div>
          )}

          {(appointment.cadastrado_por || appointment.agendado_por) && (
            <div>
              <p className={detailLabelClass}>Responsáveis</p>
              <div className={`mt-1 flex flex-col gap-1 ${detailValueClass}`}>
                {appointment.cadastrado_por && (
                  <span className="inline-flex items-center gap-1">
                    <UserIcon className="w-4 h-4 text-gray-400" />
                    <span className="leading-snug">Cadastrado por {appointment.cadastrado_por}</span>
                  </span>
                )}
                {appointment.agendado_por && (
                  <span className="inline-flex items-center gap-1">
                    <UserIcon className="w-4 h-4 text-gray-400" />
                    <span className="leading-snug">Agendado por {appointment.agendado_por}</span>
                  </span>
                )}
              </div>
            </div>
          )}

          <div>
            <p className={detailLabelClass}>Motorista</p>
            <div className={`mt-1 flex items-center gap-2 ${detailValueClass}`}>
              <UserIcon className="w-4 h-4 text-gray-400" />
              <span className="leading-snug">{driverName}</span>
            </div>
          </div>

          <div>
            <p className={detailLabelClass}>Coletor(a)</p>
            <div className={`mt-1 flex items-center gap-2 ${detailValueClass}`}>
              <UserIcon className="w-4 h-4 text-gray-400" />
              <span className="leading-snug">{collectorName}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-100 dark:border-slate-800">
        {onLogisticsPackageChange && (
          <div className="flex flex-col gap-2 mb-3 md:flex-row">
            <div className="flex-1">
              <select
                value={appointment.logistics_package_id || ''}
                onChange={(event) =>
                  onLogisticsPackageChange(
                    appointment.id,
                    event.target.value ? event.target.value : null,
                  )
                }
                className={`
                  w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-700 dark:text-slate-100 rounded px-2 py-1.5 
                  focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-indigo-400 focus:border-blue-500 dark:focus:border-indigo-400
                  ${compact ? 'text-xs' : 'text-sm'}
                `}
                aria-label="Selecionar pacote logístico"
              >
                <option value="">Sem pacote logístico</option>
                {logisticsPackages.map((logisticsPackage) => (
                  <option key={logisticsPackage.id} value={logisticsPackage.id}>
                    {logisticsPackage.nome}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end">
          <button
            onClick={handleDelete}
            className="p-1.5 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
            title="Excluir agendamento"
            type="button"
          >
            <TrashIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
