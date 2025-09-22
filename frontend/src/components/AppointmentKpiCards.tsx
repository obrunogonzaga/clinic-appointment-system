import React from 'react';

interface AppointmentKpiCardsProps {
  total: number;
  confirmed: number;
  pendingOrCancelled: number;
  isLoading?: boolean;
}

const statsConfig = [
  {
    key: 'total' as const,
    label: 'Total filtrado',
    highlightSuffix: 'agendamentos',
    accentClass: 'text-indigo-600',
  },
  {
    key: 'confirmed' as const,
    label: 'Confirmados',
    highlightSuffix: '',
    accentClass: 'text-emerald-600',
  },
  {
    key: 'pendingOrCancelled' as const,
    label: 'Pendentes / Cancelados',
    highlightSuffix: '',
    accentClass: 'text-amber-600',
  },
];

export const AppointmentKpiCards: React.FC<AppointmentKpiCardsProps> = ({
  total,
  confirmed,
  pendingOrCancelled,
  isLoading = false,
}) => {
  const values = {
    total,
    confirmed,
    pendingOrCancelled,
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {statsConfig.map(({ key }) => (
          <div key={key} className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <div className="h-4 w-24 animate-pulse rounded bg-gray-200" />
            <div className="mt-6 h-8 w-16 animate-pulse rounded bg-gray-200" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {statsConfig.map(({ key, label, highlightSuffix, accentClass }) => (
        <div
          key={key}
          className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm"
        >
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">{label}</p>
          <div className="mt-4 flex items-baseline gap-2">
            <span className={`text-3xl font-semibold ${accentClass}`}>{values[key]}</span>
            {highlightSuffix && (
              <span className="text-sm font-medium text-gray-400">{highlightSuffix}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
