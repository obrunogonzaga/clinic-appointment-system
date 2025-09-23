import type { Appointment, AppointmentViewModel } from '../types/appointment';

export type DateShortcut = 'today' | 'tomorrow' | 'thisWeek' | 'nextWeek';

export interface DateRange {
  start: Date;
  end: Date;
}

const onlyDigits = (value: string | null | undefined): string => value ? value.replace(/\D/g, '') : '';

export const maskCpf = (cpf: string | null | undefined): string => {
  const digits = onlyDigits(cpf);
  if (digits.length !== 11) {
    return cpf?.trim() || '';
  }
  return digits.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
};

const resolveCpfMasked = (appointment: Appointment): string => {
  const normalized = appointment.documento_normalizado?.cpf_formatted;
  if (normalized) {
    return normalized;
  }

  const normalizedDigits = appointment.documento_normalizado?.cpf;
  if (normalizedDigits) {
    return maskCpf(normalizedDigits);
  }

  if (appointment.cpf) {
    return maskCpf(appointment.cpf);
  }

  const fallbackDigits = onlyDigits(appointment.documento_completo);
  if (fallbackDigits.length === 11) {
    return maskCpf(fallbackDigits);
  }

  return '';
};

const resolveHealthPlan = (appointment: Appointment): string => {
  const planName = appointment.nome_convenio?.trim();
  const planNumber = appointment.numero_convenio?.trim();
  const planCard = ((appointment as { carteira_convenio?: string }).carteira_convenio || '').trim();

  if (planName && planNumber) {
    return `${planName} (${planNumber})`;
  }

  if (planName) {
    return planName;
  }

  if (planNumber) {
    return planNumber;
  }

  if (planCard) {
    return planCard;
  }

  return '';
};

export const toAppointmentViewModel = (appointment: Appointment): AppointmentViewModel => ({
  ...appointment,
  cpfMasked: resolveCpfMasked(appointment),
  healthPlanLabel: resolveHealthPlan(appointment) || '-',
});

export const filterAppointmentsBySearch = (
  appointments: AppointmentViewModel[],
  searchTerm: string,
): AppointmentViewModel[] => {
  const term = searchTerm.trim().toLowerCase();
  if (!term) {
    return appointments;
  }

  const termDigits = onlyDigits(term);

  return appointments.filter((appointment) => {
    const candidateStrings = [
      appointment.nome_paciente,
      appointment.healthPlanLabel,
      appointment.documento_completo,
      appointment.documento_normalizado?.rg_formatted,
      appointment.documento_normalizado?.cpf_formatted,
    ];

    if (candidateStrings.some((value) => value?.toLowerCase().includes(term))) {
      return true;
    }

    if (!termDigits) {
      return false;
    }

    const cpfDigits = onlyDigits(appointment.cpfMasked);
    const normalizedDigits = onlyDigits(appointment.documento_normalizado?.cpf ?? appointment.cpf);

    return (
      (cpfDigits && cpfDigits.includes(termDigits)) ||
      (normalizedDigits && normalizedDigits.includes(termDigits))
    );
  });
};

const startOfDay = (date: Date): Date => {
  const copy = new Date(date);
  copy.setHours(0, 0, 0, 0);
  return copy;
};

const endOfDay = (date: Date): Date => {
  const copy = new Date(date);
  copy.setHours(23, 59, 59, 999);
  return copy;
};

const getMonday = (date: Date): Date => {
  const day = date.getDay();
  const diff = (day === 0 ? -6 : 1) - day; // convert Sunday (0) to Monday (-6)
  const result = new Date(date);
  result.setDate(date.getDate() + diff);
  result.setHours(0, 0, 0, 0);
  return result;
};

const addDays = (date: Date, days: number): Date => {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
};

export const getDateRangeForShortcut = (shortcut: DateShortcut): DateRange => {
  const today = new Date();
  switch (shortcut) {
    case 'today': {
      return { start: startOfDay(today), end: endOfDay(today) };
    }
    case 'tomorrow': {
      const tomorrow = addDays(today, 1);
      return { start: startOfDay(tomorrow), end: endOfDay(tomorrow) };
    }
    case 'thisWeek': {
      const monday = getMonday(today);
      return { start: startOfDay(monday), end: endOfDay(addDays(monday, 6)) };
    }
    case 'nextWeek': {
      const monday = addDays(getMonday(today), 7);
      return { start: startOfDay(monday), end: endOfDay(addDays(monday, 6)) };
    }
    default:
      return { start: startOfDay(today), end: endOfDay(today) };
  }
};

export const filterAppointmentsByDateRange = (
  appointments: AppointmentViewModel[],
  range: DateRange | null,
): AppointmentViewModel[] => {
  if (!range) {
    return appointments;
  }

  return appointments.filter((appointment) => {
    if (!appointment.data_agendamento) {
      return false;
    }
    const appointmentDate = new Date(appointment.data_agendamento);
    return appointmentDate >= range.start && appointmentDate <= range.end;
  });
};

export const countAppointmentsByStatus = (
  appointments: AppointmentViewModel[],
): {
  total: number;
  confirmed: number;
  pendingOrCancelled: number;
} => {
  const total = appointments.length;
  let confirmed = 0;
  let pendingOrCancelled = 0;

  appointments.forEach((appointment) => {
    const status = appointment.status?.toLowerCase();
    if (status === 'confirmado') {
      confirmed += 1;
      return;
    }

    if (status === 'pendente' || status === 'cancelado' || status === 'cancelado pelo paciente') {
      pendingOrCancelled += 1;
      return;
    }

    if (status === 'reagendado' || status === 'em atendimento' || status === 'não compareceu') {
      pendingOrCancelled += 1;
    }
  });

  return {
    total,
    confirmed,
    pendingOrCancelled,
  };
};
