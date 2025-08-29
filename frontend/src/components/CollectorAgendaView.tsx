import {
    ChevronLeftIcon,
    ChevronRightIcon,
    ClockIcon,
    UserIcon,
} from '@heroicons/react/24/outline';
import React, { useMemo } from 'react';
import type { Appointment } from '../types/appointment';
import type { ActiveCollector } from '../types/collector';
import type { ActiveDriver } from '../types/driver';
import { AppointmentCard } from './AppointmentCard';

interface CollectorAgendaViewProps {
  appointments: Appointment[];
  collectors: ActiveCollector[];
  drivers: ActiveDriver[];
  selectedDate: Date;
  isLoading: boolean;
  onAppointmentStatusChange: (id: string, status: string) => void;
  onAppointmentDriverChange: (appointmentId: string, driverId: string) => void;
  onAppointmentCollectorChange: (appointmentId: string, collectorId: string) => void;
  onAppointmentDelete: (id: string) => void;
  onDateChange?: (date: Date) => void;
}

interface CollectorAppointments {
  collector: ActiveCollector;
  appointments: Appointment[];
}

const TIME_SLOTS = [
  '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30',
  '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
  '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
  '18:00', '18:30', '19:00', '19:30', '20:00'
];

const formatDateForComparison = (date: string): string => {
  const d = new Date(date);
  return d.toISOString().split('T')[0];
};

export const CollectorAgendaView: React.FC<CollectorAgendaViewProps> = ({
  appointments,
  collectors,
  drivers,
  selectedDate,
  isLoading,
  onAppointmentStatusChange,
  onAppointmentDriverChange,
  onAppointmentCollectorChange,
  onAppointmentDelete,
  onDateChange,
}) => {
  const selectedDateStr = useMemo(() => {
    return selectedDate.toISOString().split('T')[0];
  }, [selectedDate]);

  // Filter appointments for the selected date
  const filteredAppointments = useMemo(() => {
    return appointments.filter(appointment => {
      const appointmentDate = formatDateForComparison(appointment.data_agendamento);
      return appointmentDate === selectedDateStr;
    });
  }, [appointments, selectedDateStr]);

  // Group appointments by collector
  const collectorAppointments = useMemo(() => {
    const grouped: CollectorAppointments[] = [];
    
    // First, add collectors with appointments
    collectors.forEach(collector => {
      const collectorAppts = filteredAppointments.filter(
        appointment => appointment.collector_id === collector.id
      );
      
      if (collectorAppts.length > 0) {
        grouped.push({
          collector,
          appointments: collectorAppts.sort((a, b) => 
            a.hora_agendamento.localeCompare(b.hora_agendamento)
          )
        });
      }
    });

    // Add unassigned appointments
    const unassignedAppointments = filteredAppointments.filter(
      appointment => !appointment.collector_id || 
      !collectors.find(c => c.id === appointment.collector_id)
    );

    if (unassignedAppointments.length > 0) {
      grouped.push({
        collector: {
          id: 'unassigned',
          nome_completo: 'Não Atribuído',
          cpf: '',
          telefone: ''
        },
        appointments: unassignedAppointments.sort((a, b) => 
          a.hora_agendamento.localeCompare(b.hora_agendamento)
        )
      });
    }

    return grouped;
  }, [collectors, filteredAppointments]);

  const formatSelectedDate = (date: Date): string => {
    return date.toLocaleDateString('pt-BR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handlePreviousDay = () => {
    if (onDateChange) {
      const previousDay = new Date(selectedDate);
      previousDay.setDate(previousDay.getDate() - 1);
      onDateChange(previousDay);
    }
  };

  const handleNextDay = () => {
    if (onDateChange) {
      const nextDay = new Date(selectedDate);
      nextDay.setDate(nextDay.getDate() + 1);
      onDateChange(nextDay);
    }
  };

  const getAppointmentsForTimeSlot = (collectorId: string, timeSlot: string): Appointment[] => {
    const collectorData = collectorAppointments.find(ca => ca.collector.id === collectorId);
    if (!collectorData) return [];

    const [slotHour, slotMinute] = timeSlot.split(':').map(Number);
    const slotTime = slotHour * 60 + slotMinute;
    const nextSlotTime = slotTime + 30; // 30-minute slots

    return collectorData.appointments.filter(appointment => {
      const [hour, minute] = appointment.hora_agendamento.split(':').map(Number);
      const appointmentTime = hour * 60 + minute;
      return appointmentTime >= slotTime && appointmentTime < nextSlotTime;
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (collectorAppointments.length === 0) {
    return (
      <div className="text-center py-12">
        <ClockIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">
          Nenhum agendamento encontrado
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Não há agendamentos para {formatSelectedDate(selectedDate)}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {onDateChange && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={handlePreviousDay}
                  className="p-2 hover:bg-gray-200 rounded-md transition-colors"
                  title="Dia anterior"
                >
                  <ChevronLeftIcon className="w-4 h-4 text-gray-600" />
                </button>
                <button
                  onClick={handleNextDay}
                  className="p-2 hover:bg-gray-200 rounded-md transition-colors"
                  title="Próximo dia"
                >
                  <ChevronRightIcon className="w-4 h-4 text-gray-600" />
                </button>
              </div>
            )}
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 capitalize">
                {formatSelectedDate(selectedDate)}
              </h3>
              <p className="text-sm text-gray-600">
                {filteredAppointments.length} agendamento(s) • {collectorAppointments.length} coletora(s)
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <ClockIcon className="w-5 h-5 text-gray-400" />
            <span className="text-sm text-gray-600">
              Visualização por agenda
            </span>
          </div>
        </div>
      </div>

      {/* Agenda Grid */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <div className="inline-flex min-w-full" style={{ minWidth: `${280 + (collectorAppointments.length * 320)}px` }}>
            {/* Time Column */}
            <div className="flex-shrink-0 w-20 bg-gray-50 border-r border-gray-200">
              <div className="h-16 flex items-center justify-center border-b border-gray-200 bg-gray-100">
                <span className="text-sm font-medium text-gray-700">Horário</span>
              </div>
              {TIME_SLOTS.map(time => (
                <div
                  key={time}
                  className="min-h-[5rem] flex items-center justify-center border-b border-gray-200 text-xs font-medium text-gray-600 py-2"
                >
                  {time}
                </div>
              ))}
            </div>

            {/* Collector Columns */}
            {collectorAppointments.map(({ collector, appointments: collectorAppts }) => (
              <div key={collector.id} className="flex-shrink-0 w-80 border-r border-gray-200 last:border-r-0">
                {/* Collector Header */}
                <div className={`h-16 p-3 border-b border-gray-200 ${
                  collector.id === 'unassigned' 
                    ? 'bg-orange-50' 
                    : 'bg-gradient-to-r from-blue-50 to-indigo-50'
                }`}>
                  <div className="flex items-center space-x-2">
                    <UserIcon className={`w-4 h-4 flex-shrink-0 ${
                      collector.id === 'unassigned' 
                        ? 'text-orange-600' 
                        : 'text-blue-600'
                    }`} />
                    <div className="min-w-0 flex-1">
                      <h4 className={`text-sm font-semibold truncate ${
                        collector.id === 'unassigned' 
                          ? 'text-orange-900' 
                          : 'text-blue-900'
                      }`}>
                        {collector.nome_completo}
                      </h4>
                      <p className={`text-xs ${
                        collector.id === 'unassigned' 
                          ? 'text-orange-700' 
                          : 'text-blue-700'
                      }`}>
                        {collectorAppts.length} agendamento(s)
                      </p>
                    </div>
                  </div>
                </div>

                {/* Time Slots */}
                {TIME_SLOTS.map(timeSlot => {
                  const slotAppointments = getAppointmentsForTimeSlot(collector.id, timeSlot);
                  const hasMultiple = slotAppointments.length > 1;
                  const shouldShowAll = slotAppointments.length <= 3;
                  const displayAppointments = shouldShowAll 
                    ? slotAppointments 
                    : slotAppointments.slice(0, 2);
                  const hiddenCount = slotAppointments.length - displayAppointments.length;
                  
                  return (
                    <div
                      key={timeSlot}
                      className={`
                        min-h-[5rem] p-2 border-b border-gray-200 bg-white hover:bg-gray-50 transition-colors
                        ${slotAppointments.length > 3 ? 'max-h-40 overflow-y-auto' : ''}
                      `}
                    >
                      {slotAppointments.length > 0 ? (
                        <div className={`space-y-1 ${hasMultiple ? 'space-y-0.5' : ''}`}>
                          {displayAppointments.map(appointment => {
                            const getStatusColor = (status: string) => {
                              switch (status.toLowerCase()) {
                                case 'confirmado':
                                  return 'bg-green-100 border-green-200 text-green-900';
                                case 'cancelado':
                                  return 'bg-red-100 border-red-200 text-red-900';
                                case 'reagendado':
                                  return 'bg-yellow-100 border-yellow-200 text-yellow-900';
                                case 'concluído':
                                  return 'bg-blue-100 border-blue-200 text-blue-900';
                                case 'não compareceu':
                                  return 'bg-gray-100 border-gray-200 text-gray-900';
                                default:
                                  return 'bg-purple-100 border-purple-200 text-purple-900';
                              }
                            };

                            return (
                              <div
                                key={appointment.id}
                                className={`
                                  border rounded shadow-sm hover:shadow-md transition-all cursor-pointer
                                  ${hasMultiple ? 'p-1.5 text-xs' : 'p-2 text-xs'}
                                  ${getStatusColor(appointment.status)}
                                `}
                                title={`${appointment.nome_paciente} - ${appointment.status} - ${appointment.hora_agendamento}`}
                              >
                                <div className="flex items-center justify-between mb-1">
                                  <span className={`font-medium truncate ${hasMultiple ? 'text-xs' : ''}`}>
                                    {appointment.nome_paciente}
                                  </span>
                                  <span className={`flex-shrink-0 ml-1 ${hasMultiple ? 'text-xs' : 'text-xs'}`}>
                                    {appointment.hora_agendamento}
                                  </span>
                                </div>
                                <div className={`truncate opacity-80 ${hasMultiple ? 'text-xs' : ''}`}>
                                  {appointment.endereco_normalizado?.rua || 
                                   appointment.endereco_coleta || 
                                   appointment.nome_unidade}
                                </div>
                                {!hasMultiple && (appointment.nome_convenio || appointment.numero_convenio) && (
                                  <div className="text-xs opacity-70 mt-1 truncate">
                                    🏥 {appointment.nome_convenio || appointment.numero_convenio}
                                  </div>
                                )}
                              </div>
                            );
                          })}
                          
                          {/* Show "more" indicator if there are hidden appointments */}
                          {hiddenCount > 0 && (
                            <div className="bg-gray-100 border border-gray-300 rounded p-1.5 text-xs text-center text-gray-600 cursor-pointer hover:bg-gray-200 transition-colors">
                              <span className="font-medium">+{hiddenCount} mais</span>
                              <div className="text-xs opacity-70">agendamento(s)</div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="h-full flex items-center justify-center text-gray-400">
                          <span className="text-xs">—</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed Appointment Cards */}
      <div className="space-y-6">
        {collectorAppointments.map(({ collector, appointments: collectorAppts }) => (
          <div key={collector.id} className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center space-x-2 mb-4">
              <UserIcon className="w-5 h-5 text-gray-600" />
              <h3 className="text-lg font-semibold text-gray-900">
                {collector.nome_completo}
              </h3>
              <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
                {collectorAppts.length} agendamentos
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {collectorAppts.map(appointment => (
                <AppointmentCard
                  key={appointment.id}
                  appointment={appointment}
                  drivers={drivers}
                  collectors={collectors}
                  onStatusChange={onAppointmentStatusChange}
                  onDriverChange={onAppointmentDriverChange}
                  onCollectorChange={onAppointmentCollectorChange}
                  onDelete={onAppointmentDelete}
                  compact={true}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};