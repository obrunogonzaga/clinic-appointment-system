import type { Appointment } from './appointment';
import type { ActiveCollector } from './collector';
import type { ActiveDriver } from './driver';

export interface CalendarDay {
  date: Date;
  appointments: Appointment[];
  isCurrentMonth: boolean;
  isToday: boolean;
  isSelected: boolean;
  appointmentCount: number;
}

export interface CalendarWeek {
  days: CalendarDay[];
}

export interface CalendarMonth {
  year: number;
  month: number; // 0-based (January = 0)
  weeks: CalendarWeek[];
  totalAppointments: number;
}

export interface CalendarViewProps {
  appointments: Appointment[];
  currentDate: Date;
  selectedDate?: Date;
  onDateSelect: (date: Date) => void;
  onMonthChange: (date: Date) => void;
  onAppointmentStatusChange?: (id: string, status: string) => void;
  onAppointmentDriverChange?: (appointmentId: string, driverId: string) => void;
  onAppointmentCollectorChange?: (appointmentId: string, collectorId: string) => void;
  onAppointmentDelete?: (id: string) => void;
  drivers?: ActiveDriver[];
  collectors?: ActiveCollector[];
  isLoading?: boolean;
}

export interface DayModalProps {
  isOpen: boolean;
  onClose: () => void;
  date: Date;
  appointments: Appointment[];
  onStatusChange?: (id: string, status: string) => void;
  onDriverChange?: (appointmentId: string, driverId: string) => void;
  onCollectorChange?: (appointmentId: string, collectorId: string) => void;
  onDelete?: (id: string) => void;
  drivers?: ActiveDriver[];
  collectors?: ActiveCollector[];
}

export interface CalendarNavigationProps {
  currentDate: Date;
  onPrevMonth: () => void;
  onNextMonth: () => void;
  onToday: () => void;
}

export interface CalendarDayProps {
  day: CalendarDay;
  onClick: (date: Date) => void;
  isLoading?: boolean;
}

export interface AppointmentsByDate {
  [dateKey: string]: Appointment[]; // dateKey format: YYYY-MM-DD
}