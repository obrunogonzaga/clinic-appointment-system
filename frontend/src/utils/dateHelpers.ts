/**
 * Formats a date string to Brazilian format (dd/MM/yyyy)
 */
export const formatDate = (dateString: string): string => {
  if (!dateString) return '-';
  
  try {
    // Handle both ISO string and date-only formats
    const iso = dateString.split('T')[0] || dateString; // "YYYY-MM-DD"
    const [year, month, day] = iso.split('-');
    
    if (!year || !month || !day) return '-';
    
    return `${day}/${month}/${year}`;
  } catch (error) {
    console.warn('Error formatting date:', dateString, error);
    return '-';
  }
};

/**
 * Formats date and time together
 */
export const formatDateTime = (dateString: string, timeString?: string): string => {
  const formattedDate = formatDate(dateString);
  
  if (!timeString) return formattedDate;
  
  return `${formattedDate} às ${timeString}`;
};

/**
 * Checks if a date is today
 */
export const isToday = (dateString: string): boolean => {
  if (!dateString) return false;
  
  try {
    const inputDate = new Date(dateString);
    const today = new Date();
    
    return (
      inputDate.getDate() === today.getDate() &&
      inputDate.getMonth() === today.getMonth() &&
      inputDate.getFullYear() === today.getFullYear()
    );
  } catch (error) {
    console.warn('Error checking if date is today:', error);
    return false;
  }
};

/**
 * Checks if a date is tomorrow
 */
export const isTomorrow = (dateString: string): boolean => {
  if (!dateString) return false;
  
  try {
    const inputDate = new Date(dateString);
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    return (
      inputDate.getDate() === tomorrow.getDate() &&
      inputDate.getMonth() === tomorrow.getMonth() &&
      inputDate.getFullYear() === tomorrow.getFullYear()
    );
  } catch (error) {
    console.warn('Error checking if date is tomorrow:', error);
    return false;
  }
};

/**
 * Add days to a date
 */
export const addDays = (date: Date, days: number): Date => {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
};

/**
 * Add months to a date
 */
export const addMonths = (date: Date, months: number): Date => {
  const result = new Date(date);
  result.setMonth(result.getMonth() + months);
  return result;
};

/**
 * Subtract months from a date
 */
export const subMonths = (date: Date, months: number): Date => {
  const result = new Date(date);
  result.setMonth(result.getMonth() - months);
  return result;
};

/**
 * Get the end of month
 */
export const endOfMonth = (date: Date): Date => {
  const result = new Date(date);
  result.setMonth(result.getMonth() + 1, 0);
  result.setHours(23, 59, 59, 999);
  return result;
};

/**
 * Get the start of week (Sunday = 0)
 */
export const startOfWeek = (date: Date, weekStartsOn: number = 0): Date => {
  const result = new Date(date);
  const day = result.getDay();
  const diff = (day < weekStartsOn ? 7 : 0) + day - weekStartsOn;
  result.setDate(result.getDate() - diff);
  result.setHours(0, 0, 0, 0);
  return result;
};

/**
 * Get the end of week (Sunday = 0)
 */
export const endOfWeek = (date: Date, weekStartsOn: number = 0): Date => {
  const result = startOfWeek(date, weekStartsOn);
  result.setDate(result.getDate() + 6);
  result.setHours(23, 59, 59, 999);
  return result;
};

/**
 * Format date for display
 */
export const format = (date: Date, formatString: string): string => {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = d.getMonth() + 1;
  const day = d.getDate();
  
  const monthNames = [
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
  ];
  
  const weekDayNames = [
    'domingo', 'segunda-feira', 'terça-feira', 'quarta-feira',
    'quinta-feira', 'sexta-feira', 'sábado'
  ];
  
  const weekDayShort = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb'];
  
  switch (formatString) {
    case 'yyyy-MM-dd':
      return `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
    case 'dd/MM/yyyy':
      return `${day.toString().padStart(2, '0')}/${month.toString().padStart(2, '0')}/${year}`;
    case 'MMMM yyyy':
      return `${monthNames[d.getMonth()]} ${year}`;
    case 'MMMM':
      return monthNames[d.getMonth()];
    case 'EEE':
      return weekDayShort[d.getDay()];
    case 'EEEE':
      return weekDayNames[d.getDay()];
    case 'EEEE, dd \'de\' MMMM \'de\' yyyy':
      return `${weekDayNames[d.getDay()]}, ${day} de ${monthNames[d.getMonth()]} de ${year}`;
    default:
      return d.toLocaleDateString('pt-BR');
  }
};

/**
 * Check if two dates are the same day
 */
export const isSameDay = (date1: Date, date2: Date): boolean => {
  return (
    date1.getDate() === date2.getDate() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getFullYear() === date2.getFullYear()
  );
};

/**
 * Check if two dates are in the same month
 */
export const isSameMonth = (date1: Date, date2: Date): boolean => {
  return (
    date1.getMonth() === date2.getMonth() &&
    date1.getFullYear() === date2.getFullYear()
  );
};

/**
 * Check if date is today (using native Date)
 */
export const isTodayDate = (date: Date): boolean => {
  const today = new Date();
  return isSameDay(date, today);
};

/**
 * Check if two dates are equal
 */
export const isEqual = (date1: Date, date2: Date): boolean => {
  return date1.getTime() === date2.getTime();
};

/**
 * Parse ISO string to Date
 */
export const parseISO = (dateString: string): Date => {
  return new Date(dateString);
};