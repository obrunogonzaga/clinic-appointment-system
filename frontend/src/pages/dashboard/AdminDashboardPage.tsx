import {
  ChartBarIcon,
  ExclamationTriangleIcon,
  SignalIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import React, { useState } from 'react';
import { getAdminDashboardData } from '../../services/dashboard';
import type { AdminKpiCard } from '../../services/dashboard';

const PERIOD_OPTIONS = [
  { value: '7d', label: 'Últimos 7 dias' },
  { value: '30d', label: 'Últimos 30 dias' },
  { value: '90d', label: 'Últimos 90 dias' },
];

export const AdminDashboardPage: React.FC = () => {
  const [period, setPeriod] = useState('30d');

  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', 'admin', period],
    queryFn: () => getAdminDashboardData(period),
    staleTime: 5 * 60 * 1000,
  });

  const kpis = data?.kpis ?? [];
  const trend = data?.trend ?? [];
  const topUnits = data?.topUnits ?? [];
  const resourceUtilization = data?.resourceUtilization ?? [];
  const alerts = data?.alerts ?? [];

  return (
    <div className="space-y-8" role="region" aria-label="Dashboard Administrativo">
      <header className="space-y-2">
        <p className="text-sm font-semibold text-purple-600 uppercase tracking-wide">
          Administração
        </p>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-slate-100">
            Visão estratégica
          </h1>
          <label className="inline-flex items-center gap-2 text-sm text-gray-600 dark:text-slate-300">
            Período
            <select
              value={period}
              onChange={(event) => setPeriod(event.target.value)}
              className="rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-500"
              aria-label="Selecionar período do dashboard"
            >
              {PERIOD_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <p className="text-gray-600 dark:text-slate-300 max-w-2xl">
          KPIs consolidados, tendências e utilização de recursos para orientar decisões estratégicas do negócio.
        </p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6" aria-label="Indicadores estratégicos">
        {kpis.map((card) => (
          <article
            key={card.label}
            className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-4"
            aria-busy={isLoading}
          >
            <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-300">
              <SparklesIcon className="h-6 w-6" aria-hidden="true" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-slate-300">{card.label}</p>
              <p className="text-3xl font-semibold text-gray-900 dark:text-slate-100">
                {isLoading ? '—' : formatKpiValue(card)}
              </p>
              {typeof card.trend === 'number' ? (
                <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">
                  Variação {card.trend > 0 ? '+' : ''}
                  {card.trend}% no período
                </p>
              ) : null}
            </div>
          </article>
        ))}
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-6" aria-label="Tendências e destaques">
        <article className="xl:col-span-2 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-4">
          <header className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
                Tendência de agendamentos
              </h2>
              <p className="text-sm text-gray-600 dark:text-slate-300">
                Quantidade de agendamentos por dia no período selecionado.
              </p>
            </div>
            <ChartBarIcon className="h-6 w-6 text-purple-500" aria-hidden="true" />
          </header>

          {trend.length === 0 ? (
            <EmptyState message="Nenhum dado disponível para o período." />
          ) : (
            <TrendPreview trend={trend} loading={isLoading} />
          )}
        </article>

        <div className="space-y-6">
          <article className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              Top unidades/marcas
            </h2>
            {topUnits.length === 0 ? (
              <EmptyState message="Sem destaques registrados." compact />
            ) : (
              <ul className="space-y-3" role="list">
                {topUnits.map((unit) => (
                  <li key={unit.name} className="flex items-center justify-between gap-4">
                    <span className="text-sm font-medium text-gray-900 dark:text-slate-100">{unit.name}</span>
                    <span className="text-sm text-gray-600 dark:text-slate-300">{unit.value}</span>
                  </li>
                ))}
              </ul>
            )}
          </article>

          <article className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              Utilização de recursos
            </h2>
            {resourceUtilization.length === 0 ? (
              <EmptyState message="Sem dados de utilização." compact />
            ) : (
              <ul className="space-y-4" role="list">
                {resourceUtilization.map((resource) => (
                  <li key={resource.label} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-gray-900 dark:text-slate-100">{resource.label}</span>
                      <span className="text-gray-600 dark:text-slate-300">{resource.utilization}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-gray-100 dark:bg-slate-800">
                      <div
                        className="h-2 rounded-full bg-purple-500"
                        style={{ width: `${Math.min(100, resource.utilization)}%` }}
                        role="progressbar"
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-valuenow={Math.min(100, resource.utilization)}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </article>
        </div>
      </section>

      <section className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-4" aria-label="Alertas do sistema">
        <header className="flex items-center gap-3">
          <ExclamationTriangleIcon className="h-6 w-6 text-amber-500" aria-hidden="true" />
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              Alertas e pendências
            </h2>
            <p className="text-sm text-gray-600 dark:text-slate-300">
              Fique atento aos itens que requerem acompanhamento da equipe administrativa.
            </p>
          </div>
        </header>

        {alerts.length === 0 ? (
          <EmptyState message="Nenhum alerta ativo." compact />
        ) : (
          <ul className="space-y-4" role="list">
            {alerts.map((alert) => (
              <li key={alert.id} className="flex items-start gap-3 rounded-lg border border-amber-200 dark:border-amber-900/40 bg-amber-50 dark:bg-amber-900/10 p-4">
                <SignalIcon className="h-5 w-5 text-amber-600 mt-0.5" aria-hidden="true" />
                <p className="text-sm text-gray-800 dark:text-slate-200">{alert.message}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
};

interface TrendPreviewProps {
  trend: { date: string; value: number }[];
  loading?: boolean;
}

const TrendPreview: React.FC<TrendPreviewProps> = ({ trend, loading }) => {
  if (loading) {
    return <div className="py-12 text-center text-gray-500">Carregando tendência...</div>;
  }

  const maxValue = trend.reduce((accumulator, current) => Math.max(accumulator, current.value), 0) || 1;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-7 gap-3">
        {trend.map((point) => (
          <div key={point.date} className="flex flex-col items-center gap-2">
            <div className="w-full bg-purple-100 dark:bg-purple-900/30 rounded-md h-32 relative overflow-hidden">
              <div
                className="absolute bottom-0 left-0 right-0 bg-purple-500"
                style={{ height: `${(point.value / maxValue) * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-600 dark:text-slate-300">
              {new Date(point.date).toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
              })}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

function formatKpiValue(card: AdminKpiCard): string {
  if (typeof card.value !== 'number' || Number.isNaN(card.value)) {
    return '0';
  }

  const isRate = card.label.toLowerCase().includes('taxa');
  const formatted = Number.isInteger(card.value)
    ? card.value.toString()
    : card.value.toFixed(1);

  return isRate ? `${formatted}%` : formatted;
}

interface EmptyStateProps {
  message: string;
  compact?: boolean;
}

const EmptyState: React.FC<EmptyStateProps> = ({ message, compact = false }) => (
  <div className={`text-center ${compact ? 'py-8' : 'py-16'} text-sm text-gray-500 dark:text-slate-300`}>
    {message}
  </div>
);

export default AdminDashboardPage;
