export type AppointmentStatus =
  | 'Pendente'
  | 'Autorização'
  | 'Cadastrar'
  | 'Agendado'
  | 'Confirmado'
  | 'Coletado'
  | 'Alterar'
  | 'Cancelado'
  | 'Recoleta';

interface StatusColorConfig {
  background: string;
  text: string;
  border: string;
  badge: string;
}

const statusColorMap: Record<AppointmentStatus, StatusColorConfig> = {
  'Pendente': {
    background: 'bg-yellow-50',
    text: 'text-yellow-700',
    border: 'border-yellow-200',
    badge: 'bg-yellow-50 text-yellow-700 border-yellow-200',
  },
  'Autorização': {
    background: 'bg-indigo-50',
    text: 'text-indigo-700',
    border: 'border-indigo-200',
    badge: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  },
  'Cadastrar': {
    background: 'bg-blue-50',
    text: 'text-blue-700',
    border: 'border-blue-200',
    badge: 'bg-blue-50 text-blue-700 border-blue-200',
  },
  'Agendado': {
    background: 'bg-sky-50',
    text: 'text-sky-700',
    border: 'border-sky-200',
    badge: 'bg-sky-50 text-sky-700 border-sky-200',
  },
  'Confirmado': {
    background: 'bg-green-50',
    text: 'text-green-700',
    border: 'border-green-200',
    badge: 'bg-green-50 text-green-700 border-green-200',
  },
  'Coletado': {
    background: 'bg-emerald-50',
    text: 'text-emerald-700',
    border: 'border-emerald-200',
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  'Alterar': {
    background: 'bg-purple-50',
    text: 'text-purple-700',
    border: 'border-purple-200',
    badge: 'bg-purple-50 text-purple-700 border-purple-200',
  },
  'Cancelado': {
    background: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    badge: 'bg-red-50 text-red-700 border-red-200',
  },
  'Recoleta': {
    background: 'bg-orange-50',
    text: 'text-orange-700',
    border: 'border-orange-200',
    badge: 'bg-orange-50 text-orange-700 border-orange-200',
  },
};

export const getStatusColor = (status: string): StatusColorConfig => {
  return statusColorMap[status as AppointmentStatus] || statusColorMap['Pendente'];
};

export const getStatusBadgeClass = (status: string): string => {
  const config = getStatusColor(status);
  return `px-3 py-1.5 rounded-lg text-xs font-medium border ${config.badge}`;
};
