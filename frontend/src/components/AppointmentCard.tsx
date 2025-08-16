import {
    BuildingOfficeIcon,
    CalendarIcon,
    ClockIcon,
    PhoneIcon,
    TrashIcon,
    TruckIcon,
    UserIcon,
} from '@heroicons/react/24/outline';
import React from 'react';
import type { Appointment } from '../types/appointment';
import type { ActiveCollector } from '../types/collector';
import type { ActiveDriver } from '../types/driver';
import { formatDate } from '../utils/dateUtils';
import { getStatusBadgeClass } from '../utils/statusColors';

interface AppointmentCardProps {
  appointment: Appointment;
  drivers: ActiveDriver[];
  collectors?: ActiveCollector[];
  onStatusChange: (id: string, status: string) => void;
  onDriverChange: (appointmentId: string, driverId: string) => void;
  onCollectorChange?: (appointmentId: string, collectorId: string) => void;
  onDelete: (id: string) => void;
  compact?: boolean;
}

const statusOptions = [
  'Confirmado',
  'Cancelado', 
  'Reagendado',
  'Concluído',
  'Não Compareceu'
];

export const AppointmentCard: React.FC<AppointmentCardProps> = ({
  appointment,
  drivers,
  collectors = [],
  onStatusChange,
  onDriverChange,
  onCollectorChange,
  onDelete,
  compact = false
}) => {
  // Extract car info from carro field
  const getCarInfo = (carro?: string): string => {
    if (!carro) return '-';
    const carroRegex = /Carro:\s*([^|]+)/;
    const carroMatch = carroRegex.exec(carro);
    return carroMatch ? carroMatch[1].trim() : carro;
  };

  const handleDelete = () => {
    if (window.confirm('Tem certeza que deseja excluir este agendamento?')) {
      onDelete(appointment.id);
    }
  };

  return (
    <div className={`
      bg-white border border-gray-200 rounded-lg shadow-sm transition-all duration-200
      hover:shadow-md hover:border-gray-300
      ${compact ? 'p-3' : 'p-4'}
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
      <div className={`space-y-2 ${compact ? 'text-xs' : 'text-sm'} text-gray-600`}>
        {/* Date and Time */}
        <div className="flex items-center">
          <CalendarIcon className="w-4 h-4 mr-2 flex-shrink-0" />
          <span className="flex items-center">
            {formatDate(appointment.data_agendamento)}
            <ClockIcon className="w-3 h-3 mx-2 flex-shrink-0" />
            {appointment.hora_agendamento}
          </span>
        </div>

        {/* Unit */}
        <div className="flex items-center">
          <BuildingOfficeIcon className="w-4 h-4 mr-2 flex-shrink-0" />
          <span className="truncate">{appointment.nome_unidade}</span>
        </div>

        {/* Brand and Car */}
        <div className="flex items-center">
          <TruckIcon className="w-4 h-4 mr-2 flex-shrink-0" />
          <span className="truncate">
            {appointment.nome_marca}
            {!compact && (
              <span className="text-gray-500 ml-1">
                • {getCarInfo(appointment.carro)}
              </span>
            )}
          </span>
        </div>

        {/* Phone (only show if not compact and exists) */}
        {!compact && appointment.telefone && (
          <div className="flex items-center">
            <PhoneIcon className="w-4 h-4 mr-2 flex-shrink-0" />
            <span>{appointment.telefone}</span>
          </div>
        )}

        {/* Type of consultation (only show if not compact and exists) */}
        {!compact && appointment.tipo_consulta && (
          <div className="flex items-center">
            <span className="w-4 h-4 mr-2 flex-shrink-0 text-center">📋</span>
            <span className="truncate">{appointment.tipo_consulta}</span>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-100">
        <div className="flex gap-2 mb-3">
          {/* Driver Selection */}
          <div className="flex-1">
            <select
              value={appointment.driver_id || ''}
              onChange={(e) => onDriverChange(appointment.id, e.target.value)}
              className={`
                w-full border border-gray-300 rounded px-2 py-1.5 
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
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
                  w-full border border-gray-300 rounded px-2 py-1.5 
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
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
