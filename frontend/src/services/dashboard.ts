import { appointmentAPI } from './api';
import type {
  AdminDashboardMetricsResponse,
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
    scheduledFor: buildScheduledDateTime(
      appointment.data_agendamento,
      appointment.hora_agendamento,
    ),
    status: appointment.status ?? 'pendente',
  }));
}

function buildScheduledDateTime(
  dateValue: string | null | undefined,
  timeValue: string | null | undefined,
): string {
  if (!dateValue) {
    return '';
  }

  if (!timeValue) {
    return dateValue;
  }

  const trimmedTime = timeValue.trim();
  if (!trimmedTime) {
    return dateValue;
  }

  const datePart = dateValue.split('T')[0];
  if (!datePart) {
    return dateValue;
  }

  const timeHasSeconds = trimmedTime.split(':').length === 3;
  const normalizedTime = timeHasSeconds ? trimmedTime : `${trimmedTime}:00`;

  return `${datePart}T${normalizedTime}`;
}

export async function getOperationDashboardData(
  filter: OperationDateFilter,
): Promise<OperationDashboardData> {
  try {
    const { appointments, stats: statsRange } = buildOperationFilters(filter);
    const [dashboardStats, upcomingAppointments] = await Promise.all([
      appointmentAPI.getDashboardStats({
        start_date: statsRange.startDate,
        end_date: statsRange.endDate,
      }),
      appointmentAPI.getAppointments(appointments),
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

interface OperationFilters {
  appointments: AppointmentFilter;
  stats: { startDate: string; endDate: string };
}

function buildOperationFilters(filter: OperationDateFilter): OperationFilters {
  const baseDate = new Date();
  baseDate.setHours(0, 0, 0, 0);

  const params: AppointmentFilter = {
    page: 1,
    page_size: 50,
    scope: 'current',
  };

  const rangeStart = new Date(baseDate);

  if (filter === 'today') {
    const startDate = new Date(rangeStart);
    const endDate = new Date(rangeStart);
    endDate.setDate(endDate.getDate() + 1);

    params.data = formatAsISODate(startDate);

    return {
      appointments: params,
      stats: {
        startDate: formatAsISODate(startDate),
        endDate: formatAsISODate(endDate),
      },
    };
  }

  if (filter === 'tomorrow') {
    const startDate = new Date(rangeStart);
    startDate.setDate(startDate.getDate() + 1);
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + 1);

    params.data = formatAsISODate(startDate);

    return {
      appointments: params,
      stats: {
        startDate: formatAsISODate(startDate),
        endDate: formatAsISODate(endDate),
      },
    };
  }

  const startDate = new Date(rangeStart);
  const endDate = new Date(rangeStart);
  endDate.setDate(endDate.getDate() + 7);

  return {
    appointments: params,
    stats: {
      startDate: formatAsISODate(startDate),
      endDate: formatAsISODate(endDate),
    },
  };
}

export async function getAdminDashboardData(
  period: string,
  options?: { startDate?: string; endDate?: string }
): Promise<AdminDashboardData> {
  try {
    const metrics = await appointmentAPI.getAdminDashboardMetrics({
      period,
      start_date: options?.startDate,
      end_date: options?.endDate,
    });

    return mapAdminDashboardMetrics(metrics);
  } catch (error) {
    console.warn(
      'Falha ao carregar dados do dashboard administrativo, usando fallback.',
      error,
    );
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

function mapAdminDashboardMetrics(
  metrics: AdminDashboardMetricsResponse,
): AdminDashboardData {
  const kpis = (metrics.kpis ?? []).map((item) => ({
    label: item.label,
    value: sanitizeNumber(item.value),
    trend: typeof item.trend === 'number' ? item.trend : undefined,
  }));

  const trend = (metrics.trend ?? []).map((point) => ({
    date: point.date,
    value: point.value,
  }));

  const topUnits = (metrics.top_units ?? []).map((unit) => ({
    name: unit.name,
    value: unit.value,
  }));

  const resourceUtilization = (metrics.resource_utilization ?? []).map(
    (resource) => ({
      label: resource.label,
      utilization: sanitizeNumber(resource.utilization),
    }),
  );

  const alerts = (metrics.alerts ?? []).map((alert) => ({
    id: alert.id,
    message: alert.message,
    type: alert.type,
  }));

  return { kpis, trend, topUnits, resourceUtilization, alerts };
}

function sanitizeNumber(value: number): number {
  if (typeof value !== 'number' || Number.isNaN(value) || !Number.isFinite(value)) {
    return 0;
  }
  return Number(value.toFixed(2));
}

function formatAsISODate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}
