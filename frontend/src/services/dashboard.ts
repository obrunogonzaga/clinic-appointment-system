type OperationalRange = 'today' | 'tomorrow' | 'week';

type AdminPeriod = '7d' | '30d' | '90d';

export interface OperationalKpis {
  total: number;
  confirmed: number;
  pending: number;
  cancelled: number;
}

export interface UpcomingAppointmentItem {
  id: string;
  patientName: string;
  scheduledAt: string;
  status: 'confirmado' | 'pendente' | 'cancelado';
  location: string;
}

export interface AdminKpis {
  totalAppointments: number;
  confirmationRate: number;
  noShowRate: number;
  cancellationRate: number;
}

export interface TrendPoint {
  label: string;
  value: number;
}

export interface TopEntity {
  name: string;
  value: number;
}

export interface ResourceUtilizationItem {
  resource: string;
  utilization: number;
}

export interface DashboardAlertsItem {
  id: string;
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
}

const BASE_ALERTS: DashboardAlertsItem[] = [
  {
    id: 'import-1',
    title: 'Importação pendente',
    description: 'Arquivo "agenda_b2b.xlsx" está aguardando validação desde ontem.',
    severity: 'warning',
  },
  {
    id: 'backlog-1',
    title: 'Backlog de confirmações',
    description: '12 agendamentos aguardando confirmação manual há mais de 24h.',
    severity: 'info',
  },
];

const MOCK_TOP_UNITS: TopEntity[] = [
  { name: 'Clínica Central', value: 58 },
  { name: 'Unidade Jardins', value: 41 },
  { name: 'Unidade Paulista', value: 36 },
];

const MOCK_RESOURCE_UTILIZATION: ResourceUtilizationItem[] = [
  { resource: 'Motoristas', utilization: 0.82 },
  { resource: 'Coletoras', utilization: 0.76 },
  { resource: 'Carros', utilization: 0.65 },
];

const addDays = (date: Date, days: number): Date => {
  const next = new Date(date);
  next.setDate(date.getDate() + days);
  return next;
};

const formatDate = (date: Date): string =>
  new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
  }).format(date);

const startOfCurrentDay = () => {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return now;
};

const baseDate = startOfCurrentDay();

const createUpcomingAppointments = (range: OperationalRange): UpcomingAppointmentItem[] => {
  const appointments: UpcomingAppointmentItem[] = [];
  const totalItems = range === 'week' ? 6 : 3;

  for (let index = 0; index < totalItems; index += 1) {
    const baseScheduledDate =
      range === 'today'
        ? baseDate
        : range === 'tomorrow'
          ? addDays(baseDate, 1)
          : addDays(baseDate, index);

    const scheduledDate = new Date(baseScheduledDate);
    const hour = 8 + index * 2;
    scheduledDate.setHours(hour, index % 2 === 0 ? 0 : 30, 0, 0);

    appointments.push({
      id: `${range}-${index}`,
      patientName: `Paciente ${index + 1}`,
      scheduledAt: scheduledDate.toISOString(),
      status: index % 3 === 0 ? 'pendente' : index % 4 === 0 ? 'cancelado' : 'confirmado',
      location: index % 2 === 0 ? 'Clínica Central' : 'Unidade Jardins',
    });
  }

  return appointments;
};

const createTrendData = (period: AdminPeriod): TrendPoint[] => {
  const points = period === '7d' ? 7 : period === '30d' ? 10 : 12;
  return Array.from({ length: points })
    .map((_, index) => {
      const day = addDays(baseDate, -index);
      return {
        label: formatDate(day),
        value: Math.max(10, 60 - index * 3 + (index % 2 === 0 ? 5 : -4)),
      };
    })
    .reverse();
};

export const dashboardService = {
  async fetchOperationalKpis(): Promise<OperationalKpis> {
    return {
      total: 42,
      confirmed: 31,
      pending: 7,
      cancelled: 4,
    };
  },

  async fetchUpcomingAppointments(range: OperationalRange): Promise<UpcomingAppointmentItem[]> {
    return createUpcomingAppointments(range);
  },

  async fetchAdminKpis(period: AdminPeriod): Promise<AdminKpis> {
    return {
      totalAppointments: period === '7d' ? 328 : period === '30d' ? 1412 : 3998,
      confirmationRate: 0.82,
      noShowRate: 0.06,
      cancellationRate: 0.12,
    };
  },

  async fetchTrends(period: AdminPeriod): Promise<TrendPoint[]> {
    return createTrendData(period);
  },

  async fetchTopUnits(): Promise<TopEntity[]> {
    return MOCK_TOP_UNITS;
  },

  async fetchResourceUtilization(): Promise<ResourceUtilizationItem[]> {
    return MOCK_RESOURCE_UTILIZATION;
  },

  async fetchAlerts(): Promise<DashboardAlertsItem[]> {
    return BASE_ALERTS;
  },
};

export type { OperationalRange, AdminPeriod };
