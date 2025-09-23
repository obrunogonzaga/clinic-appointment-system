import {
  addDays,
  addMonths,
  endOfMonth,
  endOfWeek,
  format,
  isEqual,
  isSameDay,
  isSameMonth,
  isTodayDate as isToday,
  parseISO,
  startOfWeek,
  subMonths,
} from './dateHelpers';
import type { Appointment } from '../types/appointment';
import type { CalendarDay, CalendarMonth, CalendarWeek, AppointmentsByDate } from '../types/agenda';

/**
 * Gera os dados do calendário para um mês específico
 */
export function generateCalendarMonth(
  year: number,
  month: number, // 0-based
  appointments: Appointment[] = [],
  selectedDate?: Date
): CalendarMonth {
  const firstDay = new Date(year, month, 1);
  const lastDay = endOfMonth(firstDay);
  
  // Primeiro dia da primeira semana (pode ser do mês anterior)
  const startDate = startOfWeek(firstDay, 0); // Domingo
  // Último dia da última semana (pode ser do próximo mês)
  const endDate = endOfWeek(lastDay, 0);
  
  const appointmentsByDate = groupAppointmentsByDate(appointments);
  const weeks: CalendarWeek[] = [];
  let currentDate = startDate;
  
  while (currentDate <= endDate) {
    const week: CalendarWeek = { days: [] };
    
    for (let i = 0; i < 7; i++) {
      const dateKey = format(currentDate, 'yyyy-MM-dd');
      const dayAppointments = appointmentsByDate[dateKey] || [];
      
      const calendarDay: CalendarDay = {
        date: new Date(currentDate),
        appointments: dayAppointments,
        isCurrentMonth: isSameMonth(currentDate, firstDay),
        isToday: isToday(currentDate),
        isSelected: selectedDate ? isSameDay(currentDate, selectedDate) : false,
        appointmentCount: dayAppointments.length,
      };
      
      week.days.push(calendarDay);
      currentDate = addDays(currentDate, 1);
    }
    
    weeks.push(week);
  }
  
  return {
    year,
    month,
    weeks,
    totalAppointments: appointments.length,
  };
}

/**
 * Agrupa agendamentos por data (YYYY-MM-DD)
 */
export function groupAppointmentsByDate(appointments: Appointment[]): AppointmentsByDate {
  const grouped: AppointmentsByDate = {};
  
  appointments.forEach(appointment => {
    // Parse da data do agendamento
    const appointmentDate = parseISO(appointment.data_agendamento);
    const dateKey = format(appointmentDate, 'yyyy-MM-dd');
    
    if (!grouped[dateKey]) {
      grouped[dateKey] = [];
    }
    
    grouped[dateKey].push(appointment);
  });
  
  // Ordena os agendamentos de cada dia por hora
  Object.keys(grouped).forEach(dateKey => {
    grouped[dateKey].sort((a, b) => {
      const timeA = a.hora_agendamento || '00:00';
      const timeB = b.hora_agendamento || '00:00';
      return timeA.localeCompare(timeB);
    });
  });
  
  return grouped;
}

/**
 * Formata uma data para exibição
 */
export function formatCalendarDate(date: Date, formatString = 'dd/MM/yyyy'): string {
  return format(date, formatString);
}

/**
 * Formata o nome do mês e ano
 */
export function formatMonthYear(date: Date): string {
  return format(date, 'MMMM yyyy');
}

/**
 * Formata o nome do mês
 */
export function formatMonth(date: Date): string {
  return format(date, 'MMMM');
}

/**
 * Obtém os nomes dos dias da semana (Dom, Seg, Ter...)
 */
export function getWeekDayNames(short = true): string[] {
  const days = [];
  const startOfWeekDate = startOfWeek(new Date(), 0);
  
  for (let i = 0; i < 7; i++) {
    const day = addDays(startOfWeekDate, i);
    const formatted = format(day, short ? 'EEE' : 'EEEE');
    days.push(formatted.charAt(0).toUpperCase() + formatted.slice(1));
  }
  
  return days;
}

/**
 * Navega para o mês anterior
 */
export function getPreviousMonth(currentDate: Date): Date {
  return subMonths(currentDate, 1);
}

/**
 * Navega para o próximo mês
 */
export function getNextMonth(currentDate: Date): Date {
  return addMonths(currentDate, 1);
}

/**
 * Verifica se duas datas são iguais
 */
export function isSameDate(date1: Date, date2: Date): boolean {
  return isEqual(date1, date2);
}

/**
 * Obtém a cor do badge baseado no status do agendamento
 */
export function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    'Pendente': 'bg-yellow-100 text-yellow-800',
    'Autorização': 'bg-indigo-100 text-indigo-800',
    'Cadastrar': 'bg-blue-100 text-blue-800',
    'Agendado': 'bg-sky-100 text-sky-800',
    'Confirmado': 'bg-green-100 text-green-800',
    'Coletado': 'bg-emerald-100 text-emerald-800',
    'Alterar': 'bg-purple-100 text-purple-800',
    'Cancelado': 'bg-red-100 text-red-800',
    'Recoleta': 'bg-orange-100 text-orange-800',
  };
  
  return statusColors[status] || 'bg-gray-100 text-gray-800';
}

/**
 * Obtém a cor do indicador do dia baseado na quantidade de agendamentos
 */
export function getDayIndicatorColor(appointmentCount: number): string {
  if (appointmentCount === 0) return '';
  if (appointmentCount <= 2) return 'bg-green-500';
  if (appointmentCount <= 5) return 'bg-yellow-500';
  return 'bg-red-500';
}

/**
 * Filtra agendamentos para uma data específica
 */
export function getAppointmentsForDate(appointments: Appointment[], date: Date): Appointment[] {
  const dateKey = format(date, 'yyyy-MM-dd');
  const appointmentsByDate = groupAppointmentsByDate(appointments);
  return appointmentsByDate[dateKey] || [];
}

/**
 * Verifica se um dia tem agendamentos
 */
export function hasAppointments(appointments: Appointment[], date: Date): boolean {
  return getAppointmentsForDate(appointments, date).length > 0;
}
