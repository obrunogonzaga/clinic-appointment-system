export type AppointmentStatus = 
  | 'Confirmado' 
  | 'Cancelado' 
  | 'Reagendado' 
  | 'Concluído' 
  | 'Não Compareceu'
  | 'Em Atendimento';

interface StatusColorConfig {
  background: string;
  text: string;
  border: string;
  badge: string;
}

const statusColorMap: Record<AppointmentStatus, StatusColorConfig> = {
  'Confirmado': {
    background: 'bg-status-confirmed-50',
    text: 'text-status-confirmed-700',
    border: 'border-status-confirmed',
    badge: 'bg-status-confirmed-50 text-status-confirmed-700 border-status-confirmed'
  },
  'Cancelado': {
    background: 'bg-status-cancelled-50',
    text: 'text-status-cancelled-700', 
    border: 'border-status-cancelled',
    badge: 'bg-status-cancelled-50 text-status-cancelled-700 border-status-cancelled'
  },
  'Reagendado': {
    background: 'bg-status-rescheduled-50',
    text: 'text-status-rescheduled-700',
    border: 'border-status-rescheduled', 
    badge: 'bg-status-rescheduled-50 text-status-rescheduled-700 border-status-rescheduled'
  },
  'Concluído': {
    background: 'bg-status-completed-50',
    text: 'text-status-completed-700',
    border: 'border-status-completed',
    badge: 'bg-status-completed-50 text-status-completed-700 border-status-completed'
  },
  'Não Compareceu': {
    background: 'bg-status-no-show-50',
    text: 'text-status-no-show-700',
    border: 'border-status-no-show',
    badge: 'bg-status-no-show-50 text-status-no-show-700 border-status-no-show'
  },
  'Em Atendimento': {
    background: 'bg-status-in-service-50',
    text: 'text-status-in-service-700',
    border: 'border-status-in-service',
    badge: 'bg-status-in-service-50 text-status-in-service-700 border-status-in-service'
  }
};

export const getStatusColor = (status: string): StatusColorConfig => {
  return statusColorMap[status as AppointmentStatus] || statusColorMap['Não Compareceu'];
};

export const getStatusBadgeClass = (status: string): string => {
  const config = getStatusColor(status);
  return `px-3 py-1.5 rounded-lg text-xs font-medium border ${config.badge}`;
};
