import { useQuery } from '@tanstack/react-query';
import React, { useMemo, useState } from 'react';
import {
  ChartBarIcon,
  ChartPieIcon,
  ChartLineIcon,
  ShieldCheckIcon,
  BellAlertIcon,
} from '@heroicons/react/24/outline';
import { dashboardService } from '../../services/dashboard';
import type { AdminPeriod } from '../../services/dashboard';

const periodLabels: Record<AdminPeriod, string> = {
  '7d': 'Últimos 7 dias',
  '30d': 'Últimos 30 dias',
  '90d': 'Últimos 90 dias',
};

const percentageFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'percent',
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
});

export const AdminDashboardPage: React.FC = () => {
  const [period, setPeriod] = useState<AdminPeriod>('30d');

  const { data: kpis } = useQuery({
    queryKey: ['adminKpis', period],
    queryFn: () => dashboardService.fetchAdminKpis(period),
    staleTime: 60_000,
  });

  const { data: trends } = useQuery({
    queryKey: ['adminTrends', period],
    queryFn: () => dashboardService.fetchTrends(period),
    staleTime: 60_000,
  });

  const { data: topUnits } = useQuery({
    queryKey: ['adminTopUnits'],
    queryFn: () => dashboardService.fetchTopUnits(),
    staleTime: 120_000,
  });

  const { data: utilization } = useQuery({
    queryKey: ['adminResourceUtilization'],
    queryFn: () => dashboardService.fetchResourceUtilization(),
    staleTime: 120_000,
  });

  const { data: alerts } = useQuery({
    queryKey: ['adminAlerts'],
    queryFn: () => dashboardService.fetchAlerts(),
    staleTime: 15_000,
  });

  const chartPoints = useMemo(() => {
    if (!trends || trends.length === 0) {
      return '';
    }

    const maxValue = Math.max(...trends.map((point) => point.value));
    const minValue = Math.min(...trends.map((point) => point.value));
    const range = maxValue - minValue || 1;

    return trends
      .map((point, index) => {
        const x = (index / (trends.length - 1)) * 100;
        const y = 100 - ((point.value - minValue) / range) * 100;
        return `${x},${y}`;
      })
      .join(' ');
  }, [trends]);

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-wide text-purple-600">Dashboard administrativo</p>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Visão estratégica do negócio</h1>
        <p className="text-gray-600 dark:text-slate-300 max-w-2xl">
          Acompanhe tendências, performance operacional e alertas críticos para tomar decisões rápidas e alinhar a operação à
          estratégia.
        </p>
      </header>

      <section aria-labelledby="admin-kpis" className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h2 id="admin-kpis" className="text-xl font-semibold text-gray-900 dark:text-white">
            KPIs principais
          </h2>
          <div className="inline-flex items-center rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-1 text-sm shadow-sm" role="radiogroup">
            {(Object.keys(periodLabels) as AdminPeriod[]).map((value) => (
              <button
                key={value}
                type="button"
                role="radio"
                aria-checked={period === value}
                onClick={() => {
                  setPeriod(value);
                  window.dispatchEvent(
                    new CustomEvent('dashboard:period-changed', {
                      detail: { period: value },
                    }),
                  );
                }}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-purple-500 focus-visible:ring-offset-2 ${
                  period === value
                    ? 'bg-purple-600 text-white shadow'
                    : 'text-gray-600 hover:text-gray-900 dark:text-slate-300 dark:hover:text-white'
                }`}
              >
                {periodLabels[value]}
              </button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[{
            label: 'Total de agendamentos',
            value: kpis?.totalAppointments ?? 0,
            icon: ChartBarIcon,
            accent: 'bg-purple-100 text-purple-600',
          },
          {
            label: 'Taxa de confirmação',
            value: kpis?.confirmationRate ?? 0,
            icon: ChartPieIcon,
            accent: 'bg-emerald-100 text-emerald-600',
            format: percentageFormatter,
          },
          {
            label: 'No-show',
            value: kpis?.noShowRate ?? 0,
            icon: ShieldCheckIcon,
            accent: 'bg-orange-100 text-orange-600',
            format: percentageFormatter,
          },
          {
            label: 'Cancelamentos',
            value: kpis?.cancellationRate ?? 0,
            icon: BellAlertIcon,
            accent: 'bg-red-100 text-red-600',
            format: percentageFormatter,
          }].map(({ label, value, icon: Icon, accent, format }) => (
            <article
              key={label}
              className="rounded-xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-5 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-slate-400">{label}</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                    {format ? format.format(value) : value.toLocaleString('pt-BR')}
                  </p>
                </div>
                <span className={`inline-flex h-12 w-12 items-center justify-center rounded-full ${accent}`}>
                  <Icon className="h-6 w-6" aria-hidden="true" />
                </span>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section aria-labelledby="trend" className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <article className="xl:col-span-2 rounded-xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-5 shadow-sm">
          <header className="flex items-center justify-between">
            <div>
              <h2 id="trend" className="text-xl font-semibold text-gray-900 dark:text-white">
                Tendência de agendamentos
              </h2>
              <p className="text-sm text-gray-500 dark:text-slate-400">Volume diário no período selecionado</p>
            </div>
            <ChartLineIcon className="h-6 w-6 text-purple-500" aria-hidden="true" />
          </header>
          <div className="mt-6 h-56">
            {trends && trends.length > 0 ? (
              <svg viewBox="0 0 100 100" className="h-full w-full" role="img" aria-label="Gráfico de tendência de agendamentos">
                <polyline
                  fill="none"
                  strokeWidth={3}
                  stroke="url(#trendGradient)"
                  points={chartPoints}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <defs>
                  <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#7c3aed" stopOpacity="0.9" />
                    <stop offset="100%" stopColor="#c4b5fd" stopOpacity="0.5" />
                  </linearGradient>
                </defs>
                {trends.map((point, index) => (
                  <g key={point.label}>
                    <circle
                      cx={(index / (trends.length - 1)) * 100}
                      cy={100 - ((point.value - Math.min(...trends.map((p) => p.value))) /
                            (Math.max(...trends.map((p) => p.value)) - Math.min(...trends.map((p) => p.value)) || 1)) * 100}
                      r={1.5}
                      fill="#7c3aed"
                    />
                    <text
                      x={(index / (trends.length - 1)) * 100}
                      y={100}
                      textAnchor="middle"
                      dy="12"
                      fontSize="6"
                      fill="#64748b"
                    >
                      {point.label}
                    </text>
                  </g>
                ))}
              </svg>
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-gray-500 dark:text-slate-400">
                Sem dados suficientes para o período selecionado.
              </div>
            )}
          </div>
        </article>

        <article className="rounded-xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-5 shadow-sm space-y-4">
          <header>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Top unidades</h2>
            <p className="text-sm text-gray-500 dark:text-slate-400">Unidades com maior volume de agendamentos</p>
          </header>
          <ol className="space-y-3" role="list">
            {topUnits && topUnits.length > 0 ? (
              topUnits.map((unit, index) => (
                <li key={unit.name} className="flex items-center justify-between rounded-lg border border-gray-100 dark:border-slate-800 px-4 py-3">
                  <div>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">{index + 1}. {unit.name}</p>
                    <p className="text-xs text-gray-500 dark:text-slate-400">{unit.value} agendamentos</p>
                  </div>
                  <span className="text-sm font-semibold text-purple-600">{Math.round((unit.value / (topUnits[0]?.value || 1)) * 100)}%</span>
                </li>
              ))
            ) : (
              <li className="text-sm text-gray-500 dark:text-slate-400">Sem unidades ranqueadas.</li>
            )}
          </ol>
        </article>
      </section>

      <section aria-labelledby="resources" className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <article className="rounded-xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-5 shadow-sm space-y-4">
          <header>
            <h2 id="resources" className="text-xl font-semibold text-gray-900 dark:text-white">Utilização de recursos</h2>
            <p className="text-sm text-gray-500 dark:text-slate-400">Proporção de disponibilidade x demanda</p>
          </header>
          <ul className="space-y-4" role="list">
            {utilization && utilization.length > 0 ? (
              utilization.map((resource) => (
                <li key={resource.resource} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-gray-800 dark:text-slate-200">{resource.resource}</span>
                    <span className="text-gray-500 dark:text-slate-400">{percentageFormatter.format(resource.utilization)}</span>
                  </div>
                  <div className="h-2 rounded-full bg-gray-100 dark:bg-slate-800">
                    <div
                      className="h-2 rounded-full bg-purple-500"
                      style={{ width: `${Math.min(100, Math.round(resource.utilization * 100))}%` }}
                      role="presentation"
                    />
                  </div>
                </li>
              ))
            ) : (
              <li className="text-sm text-gray-500 dark:text-slate-400">Sem dados de utilização.</li>
            )}
          </ul>
        </article>

        <article className="rounded-xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-5 shadow-sm space-y-4">
          <header className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Alertas</h2>
              <p className="text-sm text-gray-500 dark:text-slate-400">Itens que exigem atenção da liderança</p>
            </div>
            <BellAlertIcon className="h-6 w-6 text-red-500" aria-hidden="true" />
          </header>
          <ul className="space-y-3" role="list">
            {alerts && alerts.length > 0 ? (
              alerts.map((alert) => (
                <li
                  key={alert.id}
                  className={`rounded-lg border px-4 py-3 text-left ${
                    alert.severity === 'critical'
                      ? 'border-red-200 bg-red-50 text-red-700'
                      : alert.severity === 'warning'
                        ? 'border-amber-200 bg-amber-50 text-amber-700'
                        : 'border-blue-200 bg-blue-50 text-blue-700'
                  }`}
                >
                  <p className="text-sm font-semibold">{alert.title}</p>
                  <p className="text-xs mt-1">{alert.description}</p>
                </li>
              ))
            ) : (
              <li className="text-sm text-gray-500 dark:text-slate-400">Nenhum alerta registrado.</li>
            )}
          </ul>
        </article>
      </section>
    </div>
  );
};
