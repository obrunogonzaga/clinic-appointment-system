import {
  ArrowPathIcon,
  ArrowRightIcon,
  CalendarDaysIcon,
  DocumentArrowUpIcon,
  ExclamationTriangleIcon,
  MapPinIcon,
  PlusIcon,
  Squares2X2Icon,
  UserGroupIcon,
  TruckIcon,
} from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardService, type OperationalDashboardData, type OperationalRange } from '../../services/dashboardService';

const FILTERS: Array<{ id: OperationalRange; label: string }> = [
  { id: 'today', label: 'Hoje' },
  { id: 'tomorrow', label: 'Amanhã' },
  { id: 'week', label: 'Semana' },
];

const toDate = (value: string): Date | null => {
  if (!value) {
    return null;
  }

  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
};

const formatDateTime = (value: string): string => {
  const parsed = toDate(value);
  if (!parsed) {
    return 'Sem horário definido';
  }

  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(parsed);
};

const filterUpcomingByRange = (
  upcoming: OperationalDashboardData['upcomingAppointments'],
  range: OperationalRange,
) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const tomorrowStart = new Date(today);
  tomorrowStart.setDate(tomorrowStart.getDate() + 1);
  const tomorrowEnd = new Date(tomorrowStart);
  tomorrowEnd.setDate(tomorrowEnd.getDate() + 1);

  const weekEnd = new Date(today);
  weekEnd.setDate(weekEnd.getDate() + 7);

  return upcoming.filter((item) => {
    const parsed = toDate(item.scheduledFor);
    if (!parsed) {
      return false;
    }

    if (range === 'tomorrow') {
      return parsed >= tomorrowStart && parsed < tomorrowEnd;
    }

    if (range === 'week') {
      return parsed >= today && parsed < weekEnd;
    }

    return parsed >= today && parsed < tomorrowStart;
  });
};

export const OperationDashboard: React.FC = () => {
  const navigate = useNavigate();
  const headingRef = useRef<HTMLHeadingElement>(null);
  const [filter, setFilter] = useState<OperationalRange>('today');

  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['dashboard', 'operation'],
    queryFn: () => dashboardService.getOperationalOverview(),
    staleTime: 60 * 1000,
  });

  useEffect(() => {
    headingRef.current?.focus();
  }, []);

  const filteredUpcoming = useMemo(() => {
    if (!data) {
      return [];
    }
    return filterUpcomingByRange(data.upcomingAppointments, filter);
  }, [data, filter]);

  const renderKpi = (label: string, value: number, accent: string, icon: JSX.Element) => (
    <div className={`rounded-2xl border ${accent} bg-white dark:bg-slate-950 p-5 shadow-sm`}
      role="group"
      aria-label={label}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 dark:text-slate-400">{label}</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-slate-100">{value}</p>
        </div>
        <span className="rounded-full bg-blue-50 dark:bg-blue-500/10 p-3 text-blue-600 dark:text-blue-200">
          {icon}
        </span>
      </div>
    </div>
  );

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  const shortcuts = [
    {
      label: 'Motoristas',
      description: 'Cadastre e acompanhe a frota',
      icon: <TruckIcon className="w-6 h-6" aria-hidden="true" />,
      path: '/cadastros/motoristas',
    },
    {
      label: 'Coletoras',
      description: 'Gerencie a equipe de coleta',
      icon: <UserGroupIcon className="w-6 h-6" aria-hidden="true" />,
      path: '/cadastros/coletoras',
    },
    {
      label: 'Carros',
      description: 'Disponibilidade e manutenção',
      icon: <TruckIcon className="w-6 h-6" aria-hidden="true" />,
      path: '/cadastros/carros',
    },
    {
      label: 'Pacotes',
      description: 'Combine recursos rapidamente',
      icon: <Squares2X2Icon className="w-6 h-6" aria-hidden="true" />,
      path: '/cadastros/pacotes',
    },
  ];

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1
          ref={headingRef}
          className="text-2xl font-bold text-gray-900 dark:text-slate-100"
          tabIndex={-1}
        >
          Dashboard Operacional
        </h1>
        <p className="text-sm text-gray-500 dark:text-slate-400">
          Visão consolidada dos agendamentos do dia e atalhos para a operação.
        </p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4" aria-label="Indicadores do dia">
        {renderKpi(
          'Agendamentos do dia',
          data?.kpis.totalToday ?? 0,
          'border-blue-100 dark:border-blue-500/20',
          <CalendarDaysIcon className="w-6 h-6" aria-hidden="true" />,
        )}
        {renderKpi(
          'Confirmados',
          data?.kpis.confirmedToday ?? 0,
          'border-green-100 dark:border-green-500/20',
          <ArrowRightIcon className="w-6 h-6" aria-hidden="true" />,
        )}
        {renderKpi(
          'Pendentes ou cancelados',
          data?.kpis.pendingOrCancelledToday ?? 0,
          'border-amber-100 dark:border-amber-500/20',
          <ExclamationTriangleIcon className="w-6 h-6" aria-hidden="true" />,
        )}
      </section>

      <section aria-label="Próximos agendamentos" className="space-y-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              Próximos agendamentos
            </h2>
            <p className="text-sm text-gray-500 dark:text-slate-400">
              Visualize os atendimentos mais próximos e priorize a confirmação.
            </p>
          </div>
          <div className="inline-flex rounded-full border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-900 p-1">
            {FILTERS.map((option) => (
              <button
                key={option.id}
                type="button"
                onClick={() => setFilter(option.id)}
                className={`px-3 py-1.5 text-sm rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                  filter === option.id
                    ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-200 shadow'
                    : 'text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-slate-200'
                }`}
                aria-pressed={filter === option.id}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm">
          {isLoading || isFetching ? (
            <div className="p-6 flex items-center gap-3 text-gray-500 dark:text-slate-400" role="status">
              <ArrowPathIcon className="w-5 h-5 animate-spin" aria-hidden="true" />
              Atualizando agendamentos...
            </div>
          ) : filteredUpcoming.length > 0 ? (
            <ul role="list" className="divide-y divide-gray-200 dark:divide-slate-800">
              {filteredUpcoming.map((appointment) => (
                <li key={appointment.id} className="p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <CalendarDaysIcon className="w-6 h-6 text-blue-500" aria-hidden="true" />
                    <div>
                      <p className="text-base font-medium text-gray-900 dark:text-slate-100">
                        {appointment.patientName}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-slate-400">
                        {formatDateTime(appointment.scheduledFor)}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-slate-400">
                    <span className="inline-flex items-center gap-1">
                      <MapPinIcon className="w-4 h-4" aria-hidden="true" />
                      {appointment.unit || 'Unidade não informada'}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <Squares2X2Icon className="w-4 h-4" aria-hidden="true" />
                      {appointment.brand || 'Marca não informada'}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <ExclamationTriangleIcon className="w-4 h-4" aria-hidden="true" />
                      {appointment.status || 'Sem status'}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-6 text-center text-sm text-gray-500 dark:text-slate-400">
              Nenhum agendamento encontrado para o período selecionado. Importe novos agendamentos ou ajuste os filtros.
            </div>
          )}

          {isError && (
            <div className="p-4 bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-200 text-sm flex items-center justify-between">
              <span>Não foi possível carregar os agendamentos. Tente novamente.</span>
              <button
                type="button"
                onClick={() => refetch()}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-md border border-red-200 dark:border-red-400 text-red-700 dark:text-red-100 hover:bg-red-100 dark:hover:bg-red-500/20"
              >
                <ArrowPathIcon className="w-4 h-4" aria-hidden="true" />
                Tentar novamente
              </button>
            </div>
          )}
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6" aria-label="Ações rápidas e atalhos">
        <div className="space-y-4">
          <div className="rounded-2xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
              Acesso rápido
            </h2>
            <p className="text-sm text-gray-500 dark:text-slate-400">
              Ganhe tempo importando lotes ou criando novos agendamentos.
            </p>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <button
                type="button"
                onClick={() => handleNavigate('/agendamentos?acao=importar')}
                className="flex items-center justify-between gap-3 rounded-xl border border-blue-100 dark:border-blue-500/20 bg-blue-50/60 dark:bg-blue-500/10 px-4 py-3 text-left text-blue-700 dark:text-blue-200 hover:bg-blue-100 dark:hover:bg-blue-500/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                <div>
                  <p className="font-semibold">Importar Excel</p>
                  <p className="text-xs text-blue-600/80 dark:text-blue-200/80">
                    Suba planilhas para atualizar a agenda
                  </p>
                </div>
                <DocumentArrowUpIcon className="w-6 h-6" aria-hidden="true" />
              </button>
              <button
                type="button"
                onClick={() => handleNavigate('/agendamentos?acao=novo')}
                className="flex items-center justify-between gap-3 rounded-xl border border-emerald-100 dark:border-emerald-500/20 bg-emerald-50/60 dark:bg-emerald-500/10 px-4 py-3 text-left text-emerald-700 dark:text-emerald-200 hover:bg-emerald-100 dark:hover:bg-emerald-500/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
              >
                <div>
                  <p className="font-semibold">Adicionar agendamento</p>
                  <p className="text-xs text-emerald-600/80 dark:text-emerald-200/80">
                    Cadastre um atendimento manualmente
                  </p>
                </div>
                <PlusIcon className="w-6 h-6" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">
            Atalhos operacionais
          </h2>
          <p className="text-sm text-gray-500 dark:text-slate-400">
            Acesse cadastros críticos da operação em um clique.
          </p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {shortcuts.map((shortcut) => (
              <button
                key={shortcut.label}
                type="button"
                onClick={() => handleNavigate(shortcut.path)}
                className="flex items-center gap-3 rounded-xl border border-gray-200 dark:border-slate-700 px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-slate-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                <span className="rounded-full bg-gray-100 dark:bg-slate-800 p-2 text-gray-700 dark:text-slate-200">
                  {shortcut.icon}
                </span>
                <div>
                  <p className="font-medium text-gray-900 dark:text-slate-100">{shortcut.label}</p>
                  <p className="text-xs text-gray-500 dark:text-slate-400">{shortcut.description}</p>
                </div>
                <ArrowRightIcon className="ml-auto w-4 h-4 text-gray-400 dark:text-slate-500" aria-hidden="true" />
              </button>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

