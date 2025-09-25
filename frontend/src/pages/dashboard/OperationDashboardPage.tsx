import { useQuery } from '@tanstack/react-query';
import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ArrowUpTrayIcon,
  CalendarDaysIcon,
  CheckCircleIcon,
  ClockIcon,
  PlusCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import { dashboardService } from '../../services/dashboard';
import type { OperationalRange } from '../../services/dashboard';

const dateTimeFormatter = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
});

const rangeLabels: Record<OperationalRange, string> = {
  today: 'Hoje',
  tomorrow: 'Amanhã',
  week: 'Semana',
};

export const OperationDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [range, setRange] = useState<OperationalRange>('today');

  const { data: kpis, isLoading: isLoadingKpis } = useQuery({
    queryKey: ['operationalKpis'],
    queryFn: () => dashboardService.fetchOperationalKpis(),
    staleTime: 30_000,
  });

  const {
    data: upcomingAppointments,
    isLoading: isLoadingUpcoming,
  } = useQuery({
    queryKey: ['upcomingAppointments', range],
    queryFn: () => dashboardService.fetchUpcomingAppointments(range),
    staleTime: 20_000,
  });

  const quickLinks = useMemo(
    () => [
      { label: 'Motoristas', to: '/cadastros/motoristas' },
      { label: 'Coletoras', to: '/cadastros/coletoras' },
      { label: 'Carros', to: '/cadastros/carros' },
      { label: 'Pacotes', to: '/cadastros/pacotes' },
    ],
    [],
  );

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-600">Dashboard de operação</p>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Tudo pronto para o dia?</h1>
        <p className="text-gray-600 dark:text-slate-300 max-w-2xl">
          Acompanhe os principais indicadores de hoje, confirme os próximos agendamentos e acesse rapidamente os cadastros
          necessários para manter a operação fluindo.
        </p>
      </header>

      <section aria-labelledby="operation-kpis" className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 id="operation-kpis" className="text-xl font-semibold text-gray-900 dark:text-white">
            KPIs do dia
          </h2>
          <span className="text-sm text-gray-500 dark:text-slate-400">
            Atualizado em tempo real
          </span>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[{
            label: 'Total agendamentos',
            value: kpis?.total ?? 0,
            icon: CalendarDaysIcon,
            accent: 'bg-blue-100 text-blue-600',
          },
          {
            label: 'Confirmados',
            value: kpis?.confirmed ?? 0,
            icon: CheckCircleIcon,
            accent: 'bg-green-100 text-green-600',
          },
          {
            label: 'Pendentes',
            value: kpis?.pending ?? 0,
            icon: ClockIcon,
            accent: 'bg-amber-100 text-amber-600',
          },
          {
            label: 'Cancelados',
            value: kpis?.cancelled ?? 0,
            icon: XCircleIcon,
            accent: 'bg-red-100 text-red-600',
          }].map(({ label, value, icon: Icon, accent }) => (
            <article
              key={label}
              className="rounded-xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-5 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-slate-400">{label}</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                    {isLoadingKpis ? '—' : value}
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

      <section aria-labelledby="upcoming-appointments" className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 id="upcoming-appointments" className="text-xl font-semibold text-gray-900 dark:text-white">
              Próximos agendamentos
            </h2>
            <p className="text-sm text-gray-500 dark:text-slate-400">
              Filtre rapidamente para priorizar confirmações e remarcações
            </p>
          </div>
          <div className="inline-flex items-center rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-1 text-sm shadow-sm" role="tablist">
            {(Object.keys(rangeLabels) as OperationalRange[]).map((value) => (
              <button
                key={value}
                type="button"
                role="tab"
                aria-selected={range === value}
                onClick={() => setRange(value)}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 ${
                  range === value
                    ? 'bg-blue-600 text-white shadow'
                    : 'text-gray-600 hover:text-gray-900 dark:text-slate-300 dark:hover:text-white'
                }`}
              >
                {rangeLabels[value]}
              </button>
            ))}
          </div>
        </div>
        <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950">
          {isLoadingUpcoming ? (
            <div className="py-16 text-center text-gray-500 dark:text-slate-400">Carregando agendamentos...</div>
          ) : upcomingAppointments && upcomingAppointments.length > 0 ? (
            <ul className="divide-y divide-gray-200 dark:divide-slate-800" role="list">
              {upcomingAppointments.map((appointment) => (
                <li key={appointment.id} className="flex flex-wrap items-center gap-4 px-6 py-4">
                  <div className="flex-1 min-w-[200px]">
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">
                      {appointment.patientName}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-slate-400">{appointment.location}</p>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-slate-300">
                    <CalendarDaysIcon className="h-5 w-5 text-blue-500" aria-hidden="true" />
                    {dateTimeFormatter.format(new Date(appointment.scheduledAt))}
                  </div>
                  <span
                    className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                      appointment.status === 'confirmado'
                        ? 'bg-green-100 text-green-700'
                        : appointment.status === 'pendente'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {appointment.status === 'confirmado'
                      ? 'Confirmado'
                      : appointment.status === 'pendente'
                        ? 'Pendente'
                        : 'Cancelado'}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="py-16 text-center space-y-3">
              <p className="text-lg font-semibold text-gray-900 dark:text-white">Sem agendamentos neste período</p>
              <p className="text-sm text-gray-500 dark:text-slate-400">
                Importe uma planilha ou cadastre um novo agendamento para começar a visualizar a agenda.
              </p>
              <div className="flex justify-center gap-3">
                <button
                  type="button"
                  onClick={() => navigate('/agendamentos')}
                  className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                >
                  <ArrowUpTrayIcon className="mr-2 h-5 w-5" />
                  Importar planilha
                </button>
                <button
                  type="button"
                  onClick={() => navigate('/agendamentos')}
                  className="inline-flex items-center rounded-md border border-blue-600 px-4 py-2 text-sm font-semibold text-blue-600 hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                >
                  <PlusCircleIcon className="mr-2 h-5 w-5" />
                  Novo agendamento
                </button>
              </div>
            </div>
          )}
        </div>
      </section>

      <section aria-labelledby="quick-actions" className="space-y-4">
        <div className="flex flex-col gap-2">
          <h2 id="quick-actions" className="text-xl font-semibold text-gray-900 dark:text-white">
            Acesso rápido
          </h2>
          <p className="text-sm text-gray-500 dark:text-slate-400">
            Importe novos agendamentos ou cadastre diretamente na plataforma
          </p>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <button
            type="button"
            onClick={() => navigate('/agendamentos')}
            className="group rounded-xl border border-dashed border-blue-300 bg-white dark:bg-slate-950 p-5 text-left shadow-sm transition hover:border-blue-400 hover:shadow"
          >
            <div className="flex items-center gap-3">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                <ArrowUpTrayIcon className="h-5 w-5" />
              </span>
              <div>
                <p className="font-semibold text-gray-900 dark:text-white">Importar planilha</p>
                <p className="text-sm text-gray-500 dark:text-slate-400">
                  Faça upload do Excel de agendamentos e valide conflitos
                </p>
              </div>
            </div>
          </button>
          <button
            type="button"
            onClick={() => navigate('/agendamentos')}
            className="group rounded-xl border border-dashed border-emerald-300 bg-white dark:bg-slate-950 p-5 text-left shadow-sm transition hover:border-emerald-400 hover:shadow"
          >
            <div className="flex items-center gap-3">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                <PlusCircleIcon className="h-5 w-5" />
              </span>
              <div>
                <p className="font-semibold text-gray-900 dark:text-white">Adicionar agendamento</p>
                <p className="text-sm text-gray-500 dark:text-slate-400">
                  Registre manualmente um novo compromisso na agenda
                </p>
              </div>
            </div>
          </button>
          {quickLinks.map((link) => (
            <Link
              key={link.label}
              to={link.to}
              className="group rounded-xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-5 shadow-sm transition hover:border-blue-400 hover:shadow"
            >
              <p className="font-semibold text-gray-900 dark:text-white">{link.label}</p>
              <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
                Gerenciar cadastro de {link.label.toLowerCase()}
              </p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
};
