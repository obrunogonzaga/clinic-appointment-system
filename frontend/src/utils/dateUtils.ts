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

export const formatDateTimeLabel = (isoString: string | null | undefined): string => {
  if (!isoString) {
    return '-';
  }

  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    return '-';
  }

  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
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
 * Parses a date input string into a local Date at midnight.
 * - Supports 'yyyy-MM-dd' (HTML date input) and 'dd/MM/yyyy' (pt-BR)
 * - Returns null when invalid
 */
export const parseLocalDateFromInput = (value: string | undefined | null): Date | null => {
  if (!value) return null;

  const trimmed = value.trim();

  // dd/MM/yyyy
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(trimmed)) {
    const [d, m, y] = trimmed.split('/').map(Number);
    if (!y || !m || !d) return null;
    return new Date(y, m - 1, d, 0, 0, 0, 0); // local midnight
  }

  // yyyy-MM-dd
  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
    const [y, m, d] = trimmed.split('-').map(Number);
    if (!y || !m || !d) return null;
    return new Date(y, m - 1, d, 0, 0, 0, 0); // local midnight
  }

  // Fallback: attempt native Date, but beware of timezone shifts
  const dt = new Date(trimmed);
  return Number.isNaN(dt.getTime()) ? null : dt;
};
