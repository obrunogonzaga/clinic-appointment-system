import React, { useState, useMemo } from 'react';
import { CalendarDay } from './CalendarDay';
import { CalendarNavigation } from './CalendarNavigation';
import { CalendarDayModal } from './CalendarDayModal';
import type { CalendarViewProps } from '../types/agenda';
import { 
  generateCalendarMonth, 
  getWeekDayNames, 
  getNextMonth, 
  getPreviousMonth,
  getAppointmentsForDate 
} from '../utils/agendaHelpers';

export const AppointmentCalendarView: React.FC<CalendarViewProps> = ({
  appointments,
  currentDate,
  selectedDate,
  onDateSelect,
  onMonthChange,
  onAppointmentStatusChange,
  onAppointmentDriverChange,
  onAppointmentCollectorChange,
  onAppointmentDelete,
  onAppointmentViewDetails,
  drivers = [],
  collectors = [],
  isLoading = false,
}) => {
  const [modalDate, setModalDate] = useState<Date | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Generate calendar data for current month
  const calendarData = useMemo(() => {
    return generateCalendarMonth(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      appointments,
      selectedDate
    );
  }, [currentDate, appointments, selectedDate]);

  const weekDayNames = useMemo(() => getWeekDayNames(true), []);

  // Handlers
  const handlePrevMonth = () => {
    const prevMonth = getPreviousMonth(currentDate);
    onMonthChange(prevMonth);
  };

  const handleNextMonth = () => {
    const nextMonth = getNextMonth(currentDate);
    onMonthChange(nextMonth);
  };

  const handleToday = () => {
    const today = new Date();
    onMonthChange(today);
    onDateSelect(today);
  };

  const handleDayClick = (date: Date) => {
    onDateSelect(date);
    
    // Get appointments for the clicked date
    const dayAppointments = getAppointmentsForDate(appointments, date);
    
    // If there are appointments, open the modal
    if (dayAppointments.length > 0) {
      setModalDate(date);
      setIsModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setModalDate(null);
  };

  // Get appointments for modal
  const modalAppointments = modalDate ? getAppointmentsForDate(appointments, modalDate) : [];

  return (
    <div className="space-y-4">
      {/* Calendar Navigation */}
      <CalendarNavigation
        currentDate={currentDate}
        onPrevMonth={handlePrevMonth}
        onNextMonth={handleNextMonth}
        onToday={handleToday}
      />

      {/* Calendar Grid */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {/* Week Day Headers */}
        <div className="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
          {weekDayNames.map((dayName, index) => (
            <div 
              key={`weekday-${index}`}
              className="p-3 text-center text-sm font-medium text-gray-700"
            >
              {dayName}
            </div>
          ))}
        </div>

        {/* Calendar Weeks */}
        <div className="divide-y divide-gray-200">
          {calendarData.weeks.map((week, weekIndex) => (
            <div 
              key={`week-${weekIndex}`}
              className="grid grid-cols-7 divide-x divide-gray-200"
            >
              {week.days.map((day, dayIndex) => (
                <CalendarDay
                  key={`day-${weekIndex}-${dayIndex}`}
                  day={day}
                  onClick={handleDayClick}
                  isLoading={isLoading}
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Calendar Statistics */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center space-x-4">
          <span>
            Total de agendamentos no mês: <strong>{calendarData.totalAppointments}</strong>
          </span>
        </div>

        <div className="flex items-center space-x-4">
          {/* Legend */}
          <div className="flex items-center space-x-2">
            <span>Legenda:</span>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span className="text-xs">1-2</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-yellow-500 rounded-full" />
              <span className="text-xs">3-5</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <span className="text-xs">6+</span>
            </div>
            <span className="text-xs ml-2">agendamentos/dia</span>
          </div>
        </div>
      </div>

      {/* Day Details Modal */}
      {modalDate && (
        <CalendarDayModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          date={modalDate}
          appointments={modalAppointments}
          onStatusChange={onAppointmentStatusChange}
          onDriverChange={onAppointmentDriverChange}
          onCollectorChange={onAppointmentCollectorChange}
          onDelete={onAppointmentDelete}
          drivers={drivers}
          collectors={collectors}
          onViewDetails={onAppointmentViewDetails}
        />
      )}
    </div>
  );
};