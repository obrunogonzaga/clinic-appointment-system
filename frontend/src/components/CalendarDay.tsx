import React from 'react';
import type { CalendarDayProps } from '../types/agenda';
import { getDayIndicatorColor } from '../utils/agendaHelpers';

export const CalendarDay: React.FC<CalendarDayProps> = ({
  day,
  onClick,
  isLoading = false,
}) => {
  const dayNumber = day.date.getDate();
  const hasAppointments = day.appointmentCount > 0;
  const indicatorColor = getDayIndicatorColor(day.appointmentCount);

  const handleClick = () => {
    if (!isLoading) {
      onClick(day.date);
    }
  };

  const baseClasses = [
    'relative',
    'aspect-square',
    'flex',
    'flex-col',
    'items-center',
    'justify-center',
    'text-sm',
    'border',
    'border-gray-100',
    'transition-all',
    'duration-200',
    'cursor-pointer',
  ];

  // Styling based on day state
  if (!day.isCurrentMonth) {
    baseClasses.push('text-gray-300', 'bg-gray-50');
  } else if (day.isToday) {
    baseClasses.push('bg-blue-50', 'text-blue-900', 'font-semibold', 'border-blue-200');
  } else {
    baseClasses.push('text-gray-900', 'bg-white');
  }

  // Selected state
  if (day.isSelected) {
    baseClasses.push('ring-2', 'ring-blue-500', 'bg-blue-100');
  }

  // Hover effects (only for current month days)
  if (day.isCurrentMonth && !isLoading) {
    baseClasses.push('hover:bg-gray-50', 'hover:border-gray-300');
  }

  // Loading state
  if (isLoading) {
    baseClasses.push('cursor-not-allowed', 'opacity-50');
  }

  return (
    <div
      className={baseClasses.join(' ')}
      onClick={handleClick}
      role="button"
      tabIndex={day.isCurrentMonth ? 0 : -1}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          handleClick();
        }
      }}
      title={hasAppointments ? 
        `${day.appointmentCount} agendamento${day.appointmentCount !== 1 ? 's' : ''}` : 
        'Nenhum agendamento'
      }
    >
      {/* Day number */}
      <span className="text-center">
        {dayNumber}
      </span>

      {/* Appointments indicator */}
      {hasAppointments && (
        <div className="flex items-center justify-center mt-1">
          {/* Dot indicator */}
          <div
            className={`w-2 h-2 rounded-full ${indicatorColor}`}
            aria-label={`${day.appointmentCount} agendamentos`}
          />
          
          {/* Count badge for days with many appointments */}
          {day.appointmentCount > 3 && (
            <span className="ml-1 text-xs font-medium text-gray-600">
              {day.appointmentCount}
            </span>
          )}
        </div>
      )}

      {/* Today indicator */}
      {day.isToday && (
        <div className="absolute top-1 right-1">
          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
        </div>
      )}

      {/* Selected state overlay */}
      {day.isSelected && (
        <div className="absolute inset-0 border-2 border-blue-500 rounded pointer-events-none" />
      )}
    </div>
  );
};