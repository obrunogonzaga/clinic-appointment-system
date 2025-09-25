import { Dialog, Transition } from '@headlessui/react';
import {
  CalendarIcon,
  ClockIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import React, { Fragment } from 'react';
import { AppointmentCard } from './AppointmentCard';
import type { DayModalProps } from '../types/agenda';
import { formatCalendarDate } from '../utils/agendaHelpers';

export const CalendarDayModal: React.FC<DayModalProps> = ({
  isOpen,
  onClose,
  date,
  appointments,
  onStatusChange,
  onLogisticsPackageChange,
  onDelete,
  drivers = [],
  collectors = [],
  logisticsPackages = [],
}) => {
  const dateString = formatCalendarDate(date, 'EEEE, dd \'de\' MMMM \'de\' yyyy');
  const hasAppointments = appointments.length > 0;

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
                      <CalendarIcon className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <Dialog.Title
                        as="h3"
                        className="text-lg font-semibold leading-6 text-gray-900 capitalize"
                      >
                        {dateString}
                      </Dialog.Title>
                      <p className="text-sm text-gray-500">
                        {hasAppointments ? (
                          `${appointments.length} agendamento${appointments.length !== 1 ? 's' : ''}`
                        ) : (
                          'Nenhum agendamento'
                        )}
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onClick={onClose}
                  >
                    <span className="sr-only">Fechar</span>
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>

                {/* Content */}
                <div className="max-h-96 overflow-y-auto">
                  {hasAppointments ? (
                    <div className="space-y-4">
                      {appointments.map((appointment) => (
                        <AppointmentCard
                          key={appointment.id}
                          appointment={appointment}
                          drivers={drivers as any[]}
                          collectors={collectors as any[]}
                          onStatusChange={onStatusChange || (() => {})}
                          logisticsPackages={logisticsPackages}
                          onLogisticsPackageChange={onLogisticsPackageChange}
                          onDelete={onDelete || (() => {})}
                          compact={true}
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                        <CalendarIcon className="w-8 h-8 text-gray-400" />
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Nenhum agendamento
                      </h3>
                      <p className="text-gray-500">
                        Não há agendamentos para este dia.
                      </p>
                    </div>
                  )}
                </div>

                {/* Footer */}
                {hasAppointments && (
                  <div className="mt-6 pt-4 border-t border-gray-200">
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-1">
                          <ClockIcon className="w-4 h-4" />
                          <span>
                            Horários: {appointments[0]?.hora_agendamento ?? 'Sem horário'} - {appointments[appointments.length - 1]?.hora_agendamento ?? 'Sem horário'}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex space-x-2">
                        {/* Summary badges */}
                        <div className="flex items-center space-x-2">
                          {/* Count by status */}
                          {(() => {
                            const statusCounts = appointments.reduce((acc, apt) => {
                              acc[apt.status] = (acc[apt.status] || 0) + 1;
                              return acc;
                            }, {} as Record<string, number>);
                            
                            return Object.entries(statusCounts).map(([status, count]) => (
                              <span
                                key={status}
                                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                              >
                                {status}: {count}
                              </span>
                            ));
                          })()}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};
