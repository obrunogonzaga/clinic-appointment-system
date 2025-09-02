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
import type { Appointment } from '../types/appointment';
import type { ActiveCar } from '../types/car';
import type { ActiveCollector } from '../types/collector';
import type { ActiveDriver } from '../types/driver';
import { formatDate } from '../utils/dateUtils';
import { getStatusBadgeClass } from '../utils/statusColors';

interface AppointmentCardProps {
  appointment: Appointment;
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
  'Confirmado',
  'Cancelado', 
  'Reagendado',
  'Concluído',
  'Não Compareceu',
  'Em Atendimento'
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

        {/* Address */}
        <div className="flex items-center">
          <BuildingOfficeIcon className="w-4 h-4 mr-2 flex-shrink-0" />
          <span className="truncate">
            {(() => {
              const street = appointment.endereco_normalizado?.rua || appointment.endereco_coleta;
              const number = appointment.endereco_normalizado?.numero;
              
              if (street) {
                return number ? `${street}, ${number}` : street;
              }
              
              return appointment.nome_unidade;
            })()}
          </span>
        </div>

        {/* Car */}
        <div className="flex items-center">
          <TruckIcon className="w-4 h-4 mr-2 flex-shrink-0" />
          <span className="truncate">
            {getCarInfo()}
          </span>
        </div>

        {/* Convênio */}
        {(appointment.nome_convenio || appointment.numero_convenio) && (
          <div className="flex items-center">
            <CreditCardIcon className="w-4 h-4 mr-2 flex-shrink-0" />
            <span className="truncate">
              {(() => {
                if (appointment.nome_convenio && appointment.numero_convenio) {
                  return `${appointment.nome_convenio} - ${appointment.numero_convenio}`;
                }
                return appointment.nome_convenio || appointment.numero_convenio;
              })()}
            </span>
          </div>
        )}

        {/* CPF/RG */}
        {(() => {
          // Priorizar CPF/RG formatados dos campos normalizados
          const cpfFormatted = appointment.documento_normalizado?.cpf_formatted;
          const rgFormatted = appointment.documento_normalizado?.rg_formatted;
          
          // Se não houver documentos normalizados, não exibir
          if (!cpfFormatted && !rgFormatted) {
            return null;
          }
          
          // Criar string com os documentos disponíveis
          const documents = [];
          if (cpfFormatted) {
            documents.push(`CPF: ${cpfFormatted}`);
          }
          if (rgFormatted) {
            documents.push(`RG: ${rgFormatted}`);
          }
          
          return (
            <div className="flex items-center">
              <IdentificationIcon className="w-4 h-4 mr-2 flex-shrink-0" />
              <span className="truncate">{documents.join(' | ')}</span>
            </div>
          );
        })()}

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

          {/* Car Selection */}
          {onCarChange && cars.length > 0 && (
            <div className="flex-1">
              <select
                value={appointment.car_id || ''}
                onChange={(e) => onCarChange(appointment.id, e.target.value)}
                className={`
                  w-full border border-gray-300 rounded px-2 py-1.5 
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
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
