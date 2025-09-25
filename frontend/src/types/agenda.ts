import type { AppointmentViewModel } from './appointment';
import type { LogisticsPackage } from './logistics-package';

export interface CalendarDay {
  date: Date;
  appointments: AppointmentViewModel[];
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
  appointments: AppointmentViewModel[];
  currentDate: Date;
  selectedDate?: Date;
  onDateSelect: (date: Date) => void;
  onMonthChange: (date: Date) => void;
  onAppointmentStatusChange?: (id: string, status: string) => void;
  onAppointmentLogisticsPackageChange?: (
    appointmentId: string,
    logisticsPackageId: string | null,
  ) => void;
  onAppointmentDelete?: (id: string) => void;
  drivers?: Array<{ id: string; nome_completo: string; cnh?: string; telefone?: string }>;
  collectors?: Array<{ id: string; nome_completo: string; cpf?: string; telefone?: string }>;
  logisticsPackages?: LogisticsPackage[];
  isLoading?: boolean;
  isReadOnly?: boolean;
}

export interface DayModalProps {
  isOpen: boolean;
  onClose: () => void;
  date: Date;
  appointments: AppointmentViewModel[];
  onStatusChange?: (id: string, status: string) => void;
  onLogisticsPackageChange?: (
    appointmentId: string,
    logisticsPackageId: string | null,
  ) => void;
  onDelete?: (id: string) => void;
  drivers?: Array<{ id: string; nome_completo: string; cnh?: string; telefone?: string }>;
  collectors?: Array<{ id: string; nome_completo: string; cpf?: string; telefone?: string }>;
  logisticsPackages?: LogisticsPackage[];
  isReadOnly?: boolean;
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
  [dateKey: string]: AppointmentViewModel[]; // dateKey format: YYYY-MM-DD
}
