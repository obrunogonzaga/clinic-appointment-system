import { appointmentAPI } from './api';
import type {
  AppointmentFilter,
  AppointmentListResponse,
  DashboardStats,
} from '../types/appointment';

export type OperationDateFilter = 'today' | 'tomorrow' | 'week';

export interface OperationDashboardKpis {
  total: number;
  confirmed: number;
  pending: number;
  cancelled: number;
}

export interface OperationDashboardAppointment {
  id: string;
  unit: string;
  brand: string;
  patient: string;
  scheduledFor: string;
  status: string;
}

export interface OperationDashboardData {
  kpis: OperationDashboardKpis;
  upcoming: OperationDashboardAppointment[];
}

export interface AdminKpiCard {
  label: string;
  value: number;
  trend?: number;
}

export interface TrendPoint {
  date: string;
  value: number;
}

export interface ResourceUtilization {
  label: string;
  utilization: number;
}

export interface AdminDashboardData {
  kpis: AdminKpiCard[];
  trend: TrendPoint[];
  topUnits: { name: string; value: number }[];
  resourceUtilization: ResourceUtilization[];
  alerts: { id: string; message: string; type: 'info' | 'warning' | 'error' }[];
}

const FALLBACK_OPERATION_DATA: OperationDashboardData = {
  kpis: {
    total: 0,
    confirmed: 0,
    pending: 0,
    cancelled: 0,
  },
  upcoming: [],
};

const FALLBACK_ADMIN_DATA: AdminDashboardData = {
  kpis: [
    { label: 'Agendamentos', value: 0 },
    { label: 'Taxa de confirmação', value: 0 },
    { label: 'No-show', value: 0 },
    { label: 'Cancelamentos', value: 0 },
  ],
  trend: [],
  topUnits: [],
  resourceUtilization: [],
  alerts: [],
};

function buildPendingValue(stats: DashboardStats['stats']): number {
  const pending = stats.total_appointments - stats.confirmed_appointments - stats.cancelled_appointments;
  return pending < 0 ? 0 : pending;
}

function normalizeUpcomingAppointments(response: AppointmentListResponse | null): OperationDashboardAppointment[] {
  if (!response?.appointments?.length) {
    return [];
  }

  return response.appointments.slice(0, 5).map((appointment) => ({
    id: appointment.id,
    unit: appointment.nome_unidade ?? 'Unidade não informada',
    brand: appointment.nome_marca ?? 'Marca não informada',
    patient: appointment.nome_paciente ?? 'Paciente não informado',
    scheduledFor: appointment.data_agendamento ?? '',
    status: appointment.status ?? 'pendente',
  }));
}

export async function getOperationDashboardData(
  filter: OperationDateFilter,
): Promise<OperationDashboardData> {
  try {
    const filters = buildOperationFilters(filter);
    const [dashboardStats, upcomingAppointments] = await Promise.all([
      appointmentAPI.getDashboardStats(),
      appointmentAPI.getAppointments(filters),
    ]);

    const stats = dashboardStats.stats;

    return {
      kpis: {
        total: stats.total_appointments,
        confirmed: stats.confirmed_appointments,
        pending: buildPendingValue(stats),
        cancelled: stats.cancelled_appointments,
      },
      upcoming: normalizeUpcomingAppointments(upcomingAppointments),
    };
  } catch (error) {
    console.warn('Falha ao carregar dados do dashboard operacional, usando fallback.', error);
    return {
      ...FALLBACK_OPERATION_DATA,
      kpis: { ...FALLBACK_OPERATION_DATA.kpis },
      upcoming: [...FALLBACK_OPERATION_DATA.upcoming],
    };
  }
}

function buildOperationFilters(filter: OperationDateFilter): AppointmentFilter {
  const baseDate = new Date();
  baseDate.setHours(0, 0, 0, 0);

  const params: AppointmentFilter = {
    page: 1,
    page_size: 50,
    scope: 'current',
  };

  if (filter === 'today') {
    params.data = formatAsISODate(baseDate);
  } else if (filter === 'tomorrow') {
    const tomorrow = new Date(baseDate);
    tomorrow.setDate(tomorrow.getDate() + 1);
    params.data = formatAsISODate(tomorrow);
  }

  return params;
}

export async function getAdminDashboardData(): Promise<AdminDashboardData> {
  try {
    const stats = await appointmentAPI.getDashboardStats();
    const normalizedKpis: AdminKpiCard[] = [
      { label: 'Agendamentos', value: stats.stats.total_appointments },
      { label: 'Taxa de confirmação', value: calculatePercentage(stats.stats.confirmed_appointments, stats.stats.total_appointments) },
      { label: 'No-show', value: 0 },
      { label: 'Cancelamentos', value: stats.stats.cancelled_appointments },
    ];

    const trend: TrendPoint[] = buildTrendPlaceholder();
    const topUnits = buildTopUnitsPlaceholder();
    const resourceUtilization = buildResourceUtilizationPlaceholder();

    return {
      kpis: normalizedKpis,
      trend,
      topUnits,
      resourceUtilization,
      alerts: [],
    };
  } catch (error) {
    console.warn('Falha ao carregar dados do dashboard administrativo, usando fallback.', error);
    return {
      ...FALLBACK_ADMIN_DATA,
      kpis: FALLBACK_ADMIN_DATA.kpis.map((item) => ({ ...item })),
      trend: [...FALLBACK_ADMIN_DATA.trend],
      topUnits: [...FALLBACK_ADMIN_DATA.topUnits],
      resourceUtilization: [...FALLBACK_ADMIN_DATA.resourceUtilization],
      alerts: [...FALLBACK_ADMIN_DATA.alerts],
    };
  }
}

function calculatePercentage(partial: number, total: number): number {
  if (total === 0) {
    return 0;
  }

  const percentage = (partial / total) * 100;
  return Math.round((percentage + Number.EPSILON) * 100) / 100;
}

function buildTrendPlaceholder(): TrendPoint[] {
  const today = startOfDay();
  return Array.from({ length: 7 }).map((_, index) => ({
    date: formatAsISODate(new Date(today.getTime() - (6 - index) * 24 * 60 * 60 * 1000)),
    value: Math.floor(Math.random() * 50) + 10,
  }));
}

function buildTopUnitsPlaceholder(): { name: string; value: number }[] {
  return [
    { name: 'Unidade Central', value: 120 },
    { name: 'Clínica Zona Sul', value: 94 },
    { name: 'Hospital Norte', value: 78 },
  ];
}

function buildResourceUtilizationPlaceholder(): ResourceUtilization[] {
  return [
    { label: 'Motoristas', utilization: 72 },
    { label: 'Coletoras', utilization: 64 },
    { label: 'Carros', utilization: 81 },
  ];
}

function startOfDay(date: Date = new Date()): Date {
  const cloned = new Date(date);
  cloned.setHours(0, 0, 0, 0);
  return cloned;
}

function formatAsISODate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}
