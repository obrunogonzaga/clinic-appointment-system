import {
  ArrowPathIcon,
  CalendarDaysIcon,
  ChartBarIcon,
  CheckCircleIcon,
  ClockIcon,
  ClipboardDocumentListIcon,
  DocumentArrowUpIcon,
  TruckIcon,
  UserIcon,
  UsersIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  getOperationDashboardData,
  type OperationDateFilter,
} from '../../services/dashboard';
import { formatDateTimeLabel } from '../../utils/dateUtils';
import { useAuth } from '../../hooks/useAuth';
import { resolveUserRole } from '../../utils/session';
import { ROLES } from '../../constants/roles';

const FILTER_LABELS: Record<OperationDateFilter, string> = {
  today: 'Hoje',
  tomorrow: 'Amanhã',
  week: 'Semana',
};

const QUICK_LINKS = [
  {
    to: '/cadastros/motoristas',
    label: 'Motoristas',
    icon: TruckIcon,
  },
  {
    to: '/cadastros/coletoras',
    label: 'Coletoras',
    icon: UsersIcon,
  },
  {
    to: '/cadastros/carros',
    label: 'Carros',
    icon: TruckIcon,
  },
  {
    to: '/cadastros/pacotes',
    label: 'Pacotes',
    icon: ClipboardDocumentListIcon,
  },
];

export const OperationDashboardPage: React.FC = () => {
  const [filter, setFilter] = useState<OperationDateFilter>('today');
  const navigate = useNavigate();
  const { user } = useAuth();
  const role = resolveUserRole(user);

  const {
    data,
    isLoading,
    isFetching,
    refetch,
  } = useQuery({
    queryKey: ['dashboard', 'operation', filter],
    queryFn: () => getOperationDashboardData(filter),
    staleTime: 60 * 1000,
  });

  const kpis = data?.kpis ?? {
    total: 0,
    confirmed: 0,
    pending: 0,
    cancelled: 0,
  };

  const upcoming = data?.upcoming ?? [];

  const handleNavigateToImport = () => {
    navigate('/agendamentos?view=upload');
  };

  const handleNavigateToCreate = () => {
    navigate('/agendamentos?view=novo');
  };

  return (
    <div className="space-y-8" role="region" aria-label="Dashboard Operacional">
      <header className="space-y-2">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-blue-600 uppercase tracking-wide">
              Operação
            </p>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-slate-100">
              Dashboard do dia
            </h1>
          </div>
          <button
            type="button"
            onClick={() => refetch()}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-200 dark:border-slate-700 px-4 py-2 text-sm font-medium text-gray-700 dark:text-slate-200 hover:bg-gray-50 dark:hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            <ArrowPathIcon
              className={`h-5 w-5 ${isFetching ? 'animate-spin' : ''}`}
            />
            Atualizar
          </button>
        </div>
        <p className="text-gray-600 dark:text-slate-300 max-w-2xl">
          Acompanhe os indicadores do dia, próximos agendamentos e acesse rapidamente as ações operacionais.
        </p>
      </header>

      <section aria-label="Filtros rápidos" className="flex flex-wrap gap-3">
        {(Object.keys(FILTER_LABELS) as OperationDateFilter[]).map((currentFilter) => {
          const isActive = filter === currentFilter;
          return (
            <button
              key={currentFilter}
              type="button"
              onClick={() => setFilter(currentFilter)}
              className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 text-gray-700 dark:text-slate-200 hover:bg-gray-50 dark:hover:bg-slate-800'
              }`}
              aria-pressed={isActive}
            >
              <ClockIcon className="h-4 w-4" />
              {FILTER_LABELS[currentFilter]}
            </button>
          );
        })}
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6" aria-label="Indicadores principais">
        <DashboardKpiCard
          title="Agendamentos do dia"
          value={kpis.total}
          icon={CalendarDaysIcon}
          loading={isLoading}
        />
        <DashboardKpiCard
          title="Confirmados"
          value={kpis.confirmed}
          icon={CheckCircleIcon}
          accent="success"
          loading={isLoading}
        />
        <DashboardKpiCard
          title="Pendentes"
          value={kpis.pending}
          icon={ClockIcon}
          accent="warning"
          loading={isLoading}
        />
        <DashboardKpiCard
          title="Cancelados"
          value={kpis.cancelled}
          icon={XCircleIcon}
          accent="error"
          loading={isLoading}
        />
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-6" aria-label="Resumo operacional">
        <div className="xl:col-span-2 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
                Próximos agendamentos
              </h2>
              <p className="text-sm text-gray-600 dark:text-slate-300">
                Lista dos próximos atendimentos conforme filtro selecionado.
              </p>
            </div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-16 text-gray-500">
              Carregando agendamentos...
            </div>
          ) : upcoming.length === 0 ? (
            <EmptyState
              title="Sem agendamentos disponíveis"
              description="Os filtros selecionados não retornaram agendamentos. Ajuste os filtros ou crie um novo agendamento."
              actionLabel="Criar agendamento"
              onAction={handleNavigateToCreate}
            />
          ) : (
            <ul className="divide-y divide-gray-200 dark:divide-slate-800" role="list">
              {upcoming.map((appointment) => (
                <li key={appointment.id} className="py-4">
                  <div className="flex items-center justify-between gap-4">
                    <div className="space-y-1">
                      <p className="text-sm font-semibold text-gray-900 dark:text-slate-100">
                        {appointment.unit}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-slate-300">
                        {appointment.brand} • {appointment.patient}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-slate-100">
                        {formatDateTimeLabel(appointment.scheduledFor)}
                      </p>
                      <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-slate-400">
                        {appointment.status}
                      </p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              Ações rápidas
            </h2>
            <div className="grid grid-cols-1 gap-3">
              <button
                type="button"
                onClick={handleNavigateToImport}
                className="flex items-center justify-between rounded-lg border border-gray-200 dark:border-slate-800 px-4 py-3 hover:bg-gray-50 dark:hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                <div className="flex items-center gap-3">
                  <DocumentArrowUpIcon className="h-5 w-5 text-blue-600" />
                  <div className="text-left">
                    <p className="text-sm font-semibold text-gray-900 dark:text-slate-100">
                      Importar Excel
                    </p>
                    <p className="text-xs text-gray-600 dark:text-slate-300">
                      Atualize agendamentos em lote
                    </p>
                  </div>
                </div>
                <ArrowPathIcon className="h-4 w-4 text-gray-400" />
              </button>
              <button
                type="button"
                onClick={handleNavigateToCreate}
                className="flex items-center justify-between rounded-lg border border-gray-200 dark:border-slate-800 px-4 py-3 hover:bg-gray-50 dark:hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                <div className="flex items-center gap-3">
                  <UserIcon className="h-5 w-5 text-blue-600" />
                  <div className="text-left">
                    <p className="text-sm font-semibold text-gray-900 dark:text-slate-100">
                      Novo agendamento
                    </p>
                    <p className="text-xs text-gray-600 dark:text-slate-300">
                      Cadastre um atendimento manualmente
                    </p>
                  </div>
                </div>
                <ArrowPathIcon className="h-4 w-4 text-gray-400" />
              </button>
              {role === ROLES.ADMIN ? (
                <button
                  type="button"
                  onClick={() => navigate('/dashboard/admin')}
                  className="flex items-center justify-between rounded-lg border border-gray-200 dark:border-slate-800 px-4 py-3 hover:bg-gray-50 dark:hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                >
                  <div className="flex items-center gap-3">
                    <ChartBarIcon className="h-5 w-5 text-blue-600" />
                    <div className="text-left">
                      <p className="text-sm font-semibold text-gray-900 dark:text-slate-100">
                        Dashboard administrativo
                      </p>
                      <p className="text-xs text-gray-600 dark:text-slate-300">
                        Acesse métricas estratégicas do negócio
                      </p>
                    </div>
                  </div>
                  <ArrowPathIcon className="h-4 w-4 text-gray-400" />
                </button>
              ) : null}
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              Atalhos de cadastros
            </h2>
            <div className="grid grid-cols-1 gap-3">
              {QUICK_LINKS.map((link) => {
                const Icon = link.icon;
                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    className="flex items-center gap-3 rounded-lg border border-gray-200 dark:border-slate-800 px-4 py-3 hover:bg-gray-50 dark:hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                  >
                    <span className="inline-flex items-center justify-center h-10 w-10 rounded-full bg-blue-50 dark:bg-blue-500/10 text-blue-600">
                      <Icon className="h-5 w-5" />
                    </span>
                    <span className="text-sm font-medium text-gray-900 dark:text-slate-100">
                      {link.label}
                    </span>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

interface DashboardKpiCardProps {
  title: string;
  value: number;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  loading?: boolean;
  accent?: 'success' | 'warning' | 'error';
}

const ACCENT_STYLES: Record<NonNullable<DashboardKpiCardProps['accent']>, string> = {
  success: 'text-green-600 bg-green-50 dark:text-green-300 dark:bg-green-900/20',
  warning: 'text-amber-600 bg-amber-50 dark:text-amber-200 dark:bg-amber-900/20',
  error: 'text-red-600 bg-red-50 dark:text-red-300 dark:bg-red-900/20',
};

const DashboardKpiCard: React.FC<DashboardKpiCardProps> = ({
  title,
  value,
  icon: Icon,
  loading = false,
  accent,
}) => {
  const iconClasses = accent ? ACCENT_STYLES[accent] : 'text-blue-600 bg-blue-50 dark:text-blue-300 dark:bg-blue-900/20';

  return (
    <article className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm p-6 space-y-4" aria-busy={loading}>
      <div className={`inline-flex items-center justify-center h-12 w-12 rounded-full ${iconClasses}`}>
        <Icon className="h-6 w-6" aria-hidden="true" />
      </div>
      <div>
        <p className="text-sm text-gray-600 dark:text-slate-300">{title}</p>
        <p className="text-3xl font-semibold text-gray-900 dark:text-slate-100">
          {loading ? '—' : value}
        </p>
      </div>
    </article>
  );
};

interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

const EmptyState: React.FC<EmptyStateProps> = ({ title, description, actionLabel, onAction }) => (
  <div className="text-center py-16 px-4 space-y-4">
    <div className="mx-auto h-14 w-14 rounded-full bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center">
      <CalendarDaysIcon className="h-7 w-7 text-blue-600 dark:text-blue-300" aria-hidden="true" />
    </div>
    <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-100">{title}</h3>
    <p className="text-sm text-gray-600 dark:text-slate-300 max-w-sm mx-auto">{description}</p>
    {actionLabel ? (
      <button
        type="button"
        onClick={onAction}
        className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500"
      >
        <UserIcon className="h-4 w-4" />
        {actionLabel}
      </button>
    ) : null}
  </div>
);

export default OperationDashboardPage;
