import {
  ArrowTrendingUpIcon,
  ChartBarIcon,
  CheckBadgeIcon,
  ExclamationCircleIcon,
  ShieldCheckIcon,
  SpeakerWaveIcon,
} from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useRef, useState } from 'react';
import {
  dashboardService,
  type AdminDashboardData,
  type AdminDashboardPeriod,
  type ResourceUtilizationSummary,
  type TrendPoint,
} from '../../services/dashboardService';

const PERIOD_OPTIONS: Array<{ id: AdminDashboardPeriod; label: string }> = [
  { id: '7d', label: '7 dias' },
  { id: '30d', label: '30 dias' },
  { id: '90d', label: '90 dias' },
];

const formatPercent = (value: number): string => `${(value * 100).toFixed(1)}%`;

const EmptyState: React.FC<{ message: string }> = ({ message }) => (
  <div className="rounded-xl border border-dashed border-gray-200 dark:border-slate-700 p-6 text-center text-sm text-gray-500 dark:text-slate-400">
    {message}
  </div>
);

const buildTrendBars = (trend: TrendPoint[]) => {
  if (trend.length === 0) {
    return [];
  }

  const maxValue = Math.max(...trend.map((item) => item.value), 1);

  return trend.map((item) => ({
    ...item,
    height: Math.max((item.value / maxValue) * 100, 4),
  }));
};

const buildUtilizationPercent = (resource: ResourceUtilizationSummary): number => {
  if (resource.total === 0) {
    return 0;
  }
  return Math.min(resource.utilized / resource.total, 1);
};

export const AdminDashboard: React.FC = () => {
  const headingRef = useRef<HTMLHeadingElement>(null);
  const [period, setPeriod] = useState<AdminDashboardPeriod>('7d');

  const { data, isLoading, isFetching } = useQuery<AdminDashboardData>({
    queryKey: ['dashboard', 'admin', period],
    queryFn: () => dashboardService.getAdminOverview(period),
    staleTime: 60 * 1000,
  });

  useEffect(() => {
    headingRef.current?.focus();
  }, []);

  const trendWithHeight = useMemo(() => buildTrendBars(data?.trend ?? []), [data]);

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
          <div>
            <h1
              ref={headingRef}
              className="text-2xl font-bold text-gray-900 dark:text-slate-100"
              tabIndex={-1}
            >
              Dashboard Administrativo
            </h1>
            <p className="text-sm text-gray-500 dark:text-slate-400">
              Acompanhe métricas estratégicas, tendências e alertas do negócio.
            </p>
          </div>
          <div className="inline-flex rounded-full border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-900 p-1">
            {PERIOD_OPTIONS.map((option) => (
              <button
                key={option.id}
                type="button"
                onClick={() => setPeriod(option.id)}
                className={`px-3 py-1.5 text-sm rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                  period === option.id
                    ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-200 shadow'
                    : 'text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-slate-200'
                }`}
                aria-pressed={period === option.id}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" aria-label="Indicadores estratégicos">
        <div className="rounded-2xl border border-blue-100 dark:border-blue-500/20 bg-white dark:bg-slate-950 p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-slate-400">Total de agendamentos</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-slate-100">
                {data?.kpis.totalAppointments ?? 0}
              </p>
            </div>
            <span className="rounded-full bg-blue-50 dark:bg-blue-500/10 p-3 text-blue-600 dark:text-blue-200">
              <ChartBarIcon className="w-6 h-6" aria-hidden="true" />
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-emerald-100 dark:border-emerald-500/20 bg-white dark:bg-slate-950 p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-slate-400">Taxa de confirmação</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-slate-100">
                {formatPercent(data?.kpis.confirmationRate ?? 0)}
              </p>
            </div>
            <span className="rounded-full bg-emerald-50 dark:bg-emerald-500/10 p-3 text-emerald-600 dark:text-emerald-200">
              <ShieldCheckIcon className="w-6 h-6" aria-hidden="true" />
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-amber-100 dark:border-amber-500/20 bg-white dark:bg-slate-950 p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-slate-400">Taxa de no-show</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-slate-100">
                {formatPercent(data?.kpis.noShowRate ?? 0)}
              </p>
            </div>
            <span className="rounded-full bg-amber-50 dark:bg-amber-500/10 p-3 text-amber-600 dark:text-amber-200">
              <SpeakerWaveIcon className="w-6 h-6" aria-hidden="true" />
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-rose-100 dark:border-rose-500/20 bg-white dark:bg-slate-950 p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-slate-400">Taxa de cancelamento</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-slate-100">
                {formatPercent(data?.kpis.cancellationRate ?? 0)}
              </p>
            </div>
            <span className="rounded-full bg-rose-50 dark:bg-rose-500/10 p-3 text-rose-600 dark:text-rose-200">
              <ExclamationCircleIcon className="w-6 h-6" aria-hidden="true" />
            </span>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6" aria-label="Tendências e destaques">
        <div className="rounded-2xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
                Tendência de agendamentos
              </h2>
              <p className="text-sm text-gray-500 dark:text-slate-400">
                Evolução do volume de agendamentos no período selecionado.
              </p>
            </div>
            <ArrowTrendingUpIcon className="w-6 h-6 text-blue-500" aria-hidden="true" />
          </div>
          <div className="mt-6 h-48">
            {trendWithHeight.length > 0 ? (
              <div className="flex h-full items-end gap-2">
                {trendWithHeight.map((point) => (
                  <div key={point.label} className="flex-1 flex flex-col items-center gap-2">
                    <div
                      className="w-full rounded-t-xl bg-blue-500/80 dark:bg-blue-400"
                      style={{ height: `${point.height}%` }}
                      aria-hidden="true"
                    />
                    <p className="text-xs font-medium text-gray-500 dark:text-slate-400">
                      {new Intl.DateTimeFormat('pt-BR', {
                        day: '2-digit',
                        month: 'short',
                      }).format(new Date(point.label))}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState message="Ainda não há dados suficientes para exibir a tendência." />
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-6 shadow-sm space-y-6">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Top unidades</h2>
            {data?.topUnits?.length ? (
              <ul role="list" className="mt-3 space-y-2">
                {data.topUnits.map((unit) => (
                  <li key={unit.label} className="flex items-center justify-between rounded-xl border border-gray-100 dark:border-slate-800 px-3 py-2 text-sm">
                    <span className="font-medium text-gray-900 dark:text-slate-100">{unit.label}</span>
                    <span className="text-gray-500 dark:text-slate-400">{unit.value} agendamentos</span>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState message="Nenhuma unidade com volume significativo no período." />
            )}
          </div>

          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Top marcas</h2>
            {data?.topBrands?.length ? (
              <ul role="list" className="mt-3 space-y-2">
                {data.topBrands.map((brand) => (
                  <li key={brand.label} className="flex items-center justify-between rounded-xl border border-gray-100 dark:border-slate-800 px-3 py-2 text-sm">
                    <span className="font-medium text-gray-900 dark:text-slate-100">{brand.label}</span>
                    <span className="text-gray-500 dark:text-slate-400">{brand.value} agendamentos</span>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState message="Nenhuma marca se destacou neste período." />
            )}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6" aria-label="Recursos e alertas">
        <div className="rounded-2xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
            Utilização de recursos
          </h2>
          <p className="text-sm text-gray-500 dark:text-slate-400">
            Acompanhe a disponibilidade da equipe operacional.
          </p>
          <div className="mt-4 space-y-4">
            {data?.resourceUtilization?.length ? (
              data.resourceUtilization.map((resource) => {
                const percent = buildUtilizationPercent(resource);
                return (
                  <div key={resource.label}>
                    <div className="flex items-center justify-between text-sm text-gray-500 dark:text-slate-400">
                      <span className="font-medium text-gray-900 dark:text-slate-100">{resource.label}</span>
                      <span>
                        {resource.utilized}/{resource.total} ({formatPercent(percent)})
                      </span>
                    </div>
                    <div className="mt-2 h-2 rounded-full bg-gray-100 dark:bg-slate-800">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-blue-600"
                        style={{ width: `${percent * 100}%` }}
                        aria-hidden="true"
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <EmptyState message="Dados de utilização indisponíveis." />
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
            Alertas e recomendações
          </h2>
          <p className="text-sm text-gray-500 dark:text-slate-400">
            Insights automáticos baseados nas métricas mais recentes.
          </p>
          <div className="mt-4 space-y-3">
            {data?.alerts?.length ? (
              data.alerts.map((alert, index) => (
                <div key={`${alert}-${index}`} className="flex items-start gap-3 rounded-xl border border-amber-100 dark:border-amber-500/30 bg-amber-50/50 dark:bg-amber-500/10 px-3 py-3 text-sm text-amber-700 dark:text-amber-100">
                  <CheckBadgeIcon className="w-5 h-5 mt-0.5" aria-hidden="true" />
                  <p>{alert}</p>
                </div>
              ))
            ) : isLoading || isFetching ? (
              <EmptyState message="Carregando alertas..." />
            ) : (
              <EmptyState message="Nenhum alerta no momento." />
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

