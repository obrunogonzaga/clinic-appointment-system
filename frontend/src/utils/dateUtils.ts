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
