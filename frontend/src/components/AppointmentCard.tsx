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
import type { ActiveCar } from '../types/car';
import type { ActiveCollector } from '../types/collector';
import type { ActiveDriver } from '../types/driver';
import { formatDate } from '../utils/dateUtils';
import { getStatusBadgeClass } from '../utils/statusColors';

interface AppointmentCardProps {
  appointment: AppointmentViewModel;
  drivers: ActiveDriver[];
  collectors?: ActiveCollector[];
  cars?: ActiveCar[];
  onStatusChange: (id: string, status: string) => void;
  onDriverChange: (appointmentId: string, driverId: string) => void;
  onCollectorChange?: (appointmentId: string, collectorId: string) => void;
  onCarChange?: (appointmentId: string, carId: string) => void;
  onDelete: (id: string) => void;
  compact?: boolean;
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
  cars = [],
  onStatusChange,
  onDriverChange,
  onCollectorChange,
  onCarChange,
  onDelete,
  compact = false
}) => {
  // Get car info from linked car or carro field
  const getCarInfo = (): string => {
    // First try to get info from linked car (car_id)
    if (appointment.car_id && cars.length > 0) {
      const linkedCar = cars.find(car => car.id === appointment.car_id);
      if (linkedCar) {
        let info = linkedCar.nome;
        if (linkedCar.placa) {
          info += ` (${linkedCar.placa})`;
        }
        return info;
      }
    }

    // Fallback to carro field (string format from Excel)
    if (appointment.carro) {
      const carroRegex = /Carro:\s*([^|]+)/;
      const carroMatch = carroRegex.exec(appointment.carro);
      return carroMatch ? carroMatch[1].trim() : appointment.carro;
    }

    return '-';
  };

  const handleDelete = () => {
    if (window.confirm('Tem certeza que deseja excluir este agendamento?')) {
      onDelete(appointment.id);
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
    <div className={`
      rounded-2xl border border-gray-100 bg-white shadow-sm transition-all duration-200
      hover:shadow-md hover:border-gray-200
      ${compact ? 'p-3' : 'p-5'}
    `}>
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

      {/* Body */}
      <div className={`mt-4 grid grid-cols-1 gap-4 ${compact ? '' : 'md:grid-cols-2'}`}>
        <div className="space-y-4">
          <div>
            <p className={detailLabelClass}>Data e horário</p>
            <div className={`mt-1 flex flex-wrap items-center gap-2 ${detailValueClass}`}>
              <span className="inline-flex items-center gap-1 rounded-full bg-gray-50 px-2 py-1 font-medium text-gray-600">
                <CalendarIcon className="w-3 h-3" />
                {formatDate(appointment.data_agendamento)}
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-gray-50 px-2 py-1 font-medium text-gray-600">
                <ClockIcon className="w-3 h-3" />
                {appointment.hora_agendamento}
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
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-100 dark:border-slate-800">
        <div className="flex flex-col gap-2 mb-3 md:flex-row">
          {/* Driver Selection */}
          <div className="flex-1">
            <select
              value={appointment.driver_id || ''}
              onChange={(e) => onDriverChange(appointment.id, e.target.value)}
              className={`
                w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-700 dark:text-slate-100 rounded px-2 py-1.5 
                focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-indigo-400 focus:border-blue-500 dark:focus:border-indigo-400
                ${compact ? 'text-xs' : 'text-sm'}
              `}
            >
              <option value="">Selecionar motorista</option>
              {drivers.map((driver) => (
                <option key={driver.id} value={driver.id}>
                  {driver.nome_completo}
                </option>
              ))}
            </select>
          </div>

          {/* Collector Selection */}
          {onCollectorChange && (
            <div className="flex-1">
              <select
                value={appointment.collector_id || ''}
                onChange={(e) => onCollectorChange(appointment.id, e.target.value)}
                className={`
                  w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-700 dark:text-slate-100 rounded px-2 py-1.5 
                  focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-indigo-400 focus:border-blue-500 dark:focus:border-indigo-400
                  ${compact ? 'text-xs' : 'text-sm'}
                `}
              >
                <option value="">Selecionar coletor</option>
                {collectors.map((collector) => (
                  <option key={collector.id} value={collector.id}>
                    {collector.nome_completo}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Car Selection */}
          {onCarChange && cars.length > 0 && (
            <div className="flex-1">
              <select
                value={appointment.car_id || ''}
                onChange={(e) => onCarChange(appointment.id, e.target.value)}
                className={`
                  w-full border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-700 dark:text-slate-100 rounded px-2 py-1.5 
                  focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-indigo-400 focus:border-blue-500 dark:focus:border-indigo-400
                  ${compact ? 'text-xs' : 'text-sm'}
                `}
              >
                <option value="">Selecionar carro</option>
                {cars.map((car) => (
                  <option key={car.id} value={car.id}>
                    {car.nome} {car.placa ? `(${car.placa})` : ''}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end">
          <button
            onClick={handleDelete}
            className="p-1.5 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
            title="Excluir agendamento"
          >
            <TrashIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
