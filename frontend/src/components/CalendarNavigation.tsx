import {
  ChevronLeftIcon,
  ChevronRightIcon,
  CalendarDaysIcon,
} from '@heroicons/react/24/outline';
import React from 'react';
import type { CalendarNavigationProps } from '../types/agenda';
import { formatMonthYear } from '../utils/agendaHelpers';

export const CalendarNavigation: React.FC<CalendarNavigationProps> = ({
  currentDate,
  onPrevMonth,
  onNextMonth,
  onToday,
}) => {
  const monthYear = formatMonthYear(currentDate);

  return (
    <div className="flex items-center justify-between py-4">
      {/* Previous Month Button */}
      <button
        onClick={onPrevMonth}
        className="flex items-center justify-center w-10 h-10 rounded-lg border border-gray-300 bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
        title="Mês anterior"
      >
        <ChevronLeftIcon className="w-5 h-5" />
      </button>

      {/* Current Month/Year Display */}
      <div className="flex items-center space-x-4">
        {/* Month and Year */}
        <h2 className="text-xl font-semibold text-gray-900 capitalize">
          {monthYear}
        </h2>

        {/* Today Button */}
        <button
          onClick={onToday}
          className="flex items-center space-x-2 px-3 py-2 rounded-lg border border-gray-300 bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
          title="Ir para hoje"
        >
          <CalendarDaysIcon className="w-4 h-4" />
          <span className="text-sm font-medium">Hoje</span>
        </button>
      </div>

      {/* Next Month Button */}
      <button
        onClick={onNextMonth}
        className="flex items-center justify-center w-10 h-10 rounded-lg border border-gray-300 bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
        title="Próximo mês"
      >
        <ChevronRightIcon className="w-5 h-5" />
      </button>
    </div>
  );
};