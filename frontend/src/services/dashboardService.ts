import { appointmentAPI, carAPI, collectorAPI, driverAPI } from './api';
import type { Appointment } from '../types/appointment';

type AppointmentStatusSummary = {
  total: number;
  confirmed: number;
  cancelled: number;
  pending: number;
  noShow: number;
};

export type OperationalRange = 'today' | 'tomorrow' | 'week';

export interface UpcomingAppointmentSummary {
  id: string;
  patientName: string;
  brand: string;
  unit: string;
  scheduledFor: string;
  status: string;
}

export interface OperationalDashboardData {
  kpis: {
    totalToday: number;
    confirmedToday: number;
    pendingOrCancelledToday: number;
  };
  upcomingAppointments: UpcomingAppointmentSummary[];
  lastUpdated: string;
}

export type AdminDashboardPeriod = '7d' | '30d' | '90d';

export interface TrendPoint {
  label: string;
  value: number;
}

export interface RankedItem {
  label: string;
  value: number;
}

export interface ResourceUtilizationSummary {
  label: string;
  utilized: number;
  total: number;
}

export interface AdminDashboardData {
  kpis: {
    totalAppointments: number;
    confirmationRate: number;
    noShowRate: number;
    cancellationRate: number;
  };
  trend: TrendPoint[];
  topUnits: RankedItem[];
  topBrands: RankedItem[];
  resourceUtilization: ResourceUtilizationSummary[];
  alerts: string[];
  lastUpdated: string;
}

const parseDate = (value?: string | null, time?: string | null): Date | null => {
  if (!value) {
    return null;
  }

  const isoCandidate = time ? `${value}T${time}` : `${value}T00:00:00`;
  const parsed = new Date(isoCandidate);

  return Number.isNaN(parsed.getTime()) ? null : parsed;
};

const normalizeStatus = (status?: string | null): string =>
  (status ?? '').toLowerCase();

const summarizeStatuses = (appointments: Appointment[]): AppointmentStatusSummary => {
  return appointments.reduce<AppointmentStatusSummary>((accumulator, appointment) => {
    const normalized = normalizeStatus(appointment.status);

    accumulator.total += 1;

    if (normalized.includes('confirm')) {
      accumulator.confirmed += 1;
    } else if (normalized.includes('cancel')) {
      accumulator.cancelled += 1;
    } else if (normalized.includes('no') && normalized.includes('show')) {
      accumulator.noShow += 1;
    } else {
      accumulator.pending += 1;
    }

    return accumulator;
  }, {
    total: 0,
    confirmed: 0,
    cancelled: 0,
    pending: 0,
    noShow: 0,
  });
};

const sortBySchedule = (appointments: Appointment[]): Appointment[] => {
  return [...appointments].sort((first, second) => {
    const firstDate = parseDate(first.data_agendamento ?? undefined, first.hora_agendamento ?? undefined);
    const secondDate = parseDate(second.data_agendamento ?? undefined, second.hora_agendamento ?? undefined);

    if (!firstDate && !secondDate) {
      return 0;
    }

    if (!firstDate) {
      return 1;
    }

    if (!secondDate) {
      return -1;
    }

    return firstDate.getTime() - secondDate.getTime();
  });
};

const isWithinRange = (date: Date, range: OperationalRange): boolean => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const target = new Date(today);

  if (range === 'tomorrow') {
    target.setDate(target.getDate() + 1);
    return date >= target && date < new Date(target.getTime() + 24 * 60 * 60 * 1000);
  }

  if (range === 'week') {
    const weekEnd = new Date(today);
    weekEnd.setDate(weekEnd.getDate() + 7);
    return date >= today && date < weekEnd;
  }

  return date >= today && date < new Date(today.getTime() + 24 * 60 * 60 * 1000);
};

const buildUpcomingAppointments = (
  appointments: Appointment[],
  limit = 6,
): UpcomingAppointmentSummary[] => {
  return sortBySchedule(appointments)
    .slice(0, limit)
    .map((appointment) => {
      const parsed = parseDate(
        appointment.data_agendamento ?? undefined,
        appointment.hora_agendamento ?? undefined,
      );
      return {
        id: appointment.id,
        patientName: appointment.nome_paciente,
        brand: appointment.nome_marca,
        unit: appointment.nome_unidade,
        scheduledFor: parsed ? parsed.toISOString() : '',
        status: appointment.status,
      };
    });
};

const buildRank = (appointments: Appointment[], key: 'nome_unidade' | 'nome_marca'): RankedItem[] => {
  const counter = new Map<string, number>();

  appointments.forEach((appointment) => {
    const identifier = (appointment[key] ?? 'Não informado').trim();
    counter.set(identifier, (counter.get(identifier) ?? 0) + 1);
  });

  return Array.from(counter.entries())
    .map(([label, value]) => ({ label, value }))
    .sort((first, second) => second.value - first.value)
    .slice(0, 5);
};

const buildTrend = (appointments: Appointment[]): TrendPoint[] => {
  const grouped = new Map<string, number>();

  appointments.forEach((appointment) => {
    const parsed = parseDate(
      appointment.data_agendamento ?? undefined,
      appointment.hora_agendamento ?? undefined,
    );

    if (!parsed) {
      return;
    }

    const key = parsed.toISOString().slice(0, 10);
    grouped.set(key, (grouped.get(key) ?? 0) + 1);
  });

  return Array.from(grouped.entries())
    .sort(([firstKey], [secondKey]) => (firstKey > secondKey ? 1 : -1))
    .map(([label, value]) => ({ label, value }));
};

export const dashboardService = {
  async getOperationalOverview(): Promise<OperationalDashboardData> {
    try {
      const response = await appointmentAPI.getAppointments({
        scope: 'current',
        page: 1,
        page_size: 200,
      });

      const appointments = response.appointments ?? [];

      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const todaysAppointments = appointments.filter((appointment) => {
        const parsed = parseDate(
          appointment.data_agendamento ?? undefined,
          appointment.hora_agendamento ?? undefined,
        );
        if (!parsed) {
          return false;
        }
        parsed.setHours(0, 0, 0, 0);
        return parsed.getTime() === today.getTime();
      });

      const statusSummary = summarizeStatuses(todaysAppointments);

      const upcoming = appointments.filter((appointment) => {
        const parsed = parseDate(
          appointment.data_agendamento ?? undefined,
          appointment.hora_agendamento ?? undefined,
        );
        if (!parsed) {
          return false;
        }
        return parsed >= today;
      });

      return {
        kpis: {
          totalToday: statusSummary.total,
          confirmedToday: statusSummary.confirmed,
          pendingOrCancelledToday: statusSummary.pending + statusSummary.cancelled,
        },
        upcomingAppointments: buildUpcomingAppointments(upcoming),
        lastUpdated: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Failed to compute operational dashboard', error);
      return {
        kpis: {
          totalToday: 0,
          confirmedToday: 0,
          pendingOrCancelledToday: 0,
        },
        upcomingAppointments: [],
        lastUpdated: new Date().toISOString(),
      };
    }
  },

  async getAdminOverview(period: AdminDashboardPeriod): Promise<AdminDashboardData> {
    try {
      const [appointmentsResponse, driverStatsResponse, collectorStatsResponse, carStatsResponse] =
        await Promise.all([
          appointmentAPI.getAppointments({
            scope: 'current',
            page: 1,
            page_size: 500,
          }),
          driverAPI.getDriverStats(),
          collectorAPI.getCollectorStats(),
          carAPI.getCarStats(),
        ]);

      const appointments = appointmentsResponse.appointments ?? [];

      const startDate = new Date();
      startDate.setHours(0, 0, 0, 0);

      if (period === '30d') {
        startDate.setDate(startDate.getDate() - 30);
      } else if (period === '90d') {
        startDate.setDate(startDate.getDate() - 90);
      } else {
        startDate.setDate(startDate.getDate() - 7);
      }

      const filteredAppointments = appointments.filter((appointment) => {
        const parsed = parseDate(
          appointment.data_agendamento ?? undefined,
          appointment.hora_agendamento ?? undefined,
        );

        if (!parsed) {
          return false;
        }

        return parsed >= startDate;
      });

      const statusSummary = summarizeStatuses(filteredAppointments);
      const total = Math.max(statusSummary.total, 1);

      const resourceUtilization: ResourceUtilizationSummary[] = [
        {
          label: 'Motoristas',
          utilized: driverStatsResponse.stats.active_drivers,
          total: driverStatsResponse.stats.total_drivers,
        },
        {
          label: 'Coletoras',
          utilized: collectorStatsResponse.stats.active_collectors ?? collectorStatsResponse.stats.total_collectors,
          total: collectorStatsResponse.stats.total_collectors,
        },
        {
          label: 'Carros',
          utilized: carStatsResponse.stats.active_cars ?? carStatsResponse.stats.total_cars,
          total: carStatsResponse.stats.total_cars,
        },
      ];

      const alerts: string[] = [];

      const confirmationRate = statusSummary.confirmed / total;
      const cancellationRate = statusSummary.cancelled / total;
      const noShowRate = statusSummary.noShow / total;

      if (cancellationRate > 0.2) {
        alerts.push('Taxa de cancelamentos acima do esperado. Revise confirmações e comunicação com pacientes.');
      }

      if (noShowRate > 0.1) {
        alerts.push('Há indícios de aumento em no-shows. Considere reforçar lembretes e confirmações.');
      }

      if (resourceUtilization.some((resource) => resource.utilized / Math.max(resource.total, 1) > 0.85)) {
        alerts.push('Utilização de recursos operacionais acima de 85%. Avalie expansão ou remanejamento da equipe.');
      }

      if (alerts.length === 0) {
        alerts.push('Nenhum alerta crítico no momento. Mantenha o acompanhamento das métricas.');
      }

      return {
        kpis: {
          totalAppointments: statusSummary.total,
          confirmationRate,
          noShowRate,
          cancellationRate,
        },
        trend: buildTrend(filteredAppointments),
        topUnits: buildRank(filteredAppointments, 'nome_unidade'),
        topBrands: buildRank(filteredAppointments, 'nome_marca'),
        resourceUtilization,
        alerts,
        lastUpdated: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Failed to compute admin dashboard', error);
      return {
        kpis: {
          totalAppointments: 0,
          confirmationRate: 0,
          noShowRate: 0,
          cancellationRate: 0,
        },
        trend: [],
        topUnits: [],
        topBrands: [],
        resourceUtilization: [],
        alerts: ['Não foi possível carregar as métricas estratégicas. Tente novamente mais tarde.'],
        lastUpdated: new Date().toISOString(),
      };
    }
  },
};

