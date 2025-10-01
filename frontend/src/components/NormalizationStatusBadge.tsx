import React from 'react';
import {
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  MinusCircleIcon,
} from '@heroicons/react/24/outline';

export interface NormalizationStatusBadgeProps {
  status?: 'pending' | 'processing' | 'completed' | 'failed' | 'skipped';
  error?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md';
}

export const NormalizationStatusBadge: React.FC<NormalizationStatusBadgeProps> = ({
  status,
  error,
  showLabel = true,
  size = 'sm',
}) => {
  if (!status) {
    return null;
  }

  const iconSize = size === 'sm' ? 'h-4 w-4' : 'h-5 w-5';
  const textSize = size === 'sm' ? 'text-xs' : 'text-sm';
  const padding = size === 'sm' ? 'px-2 py-0.5' : 'px-2.5 py-1';

  const statusConfig = {
    pending: {
      icon: ClockIcon,
      label: 'Aguardando',
      color: 'bg-yellow-50 text-yellow-700 border-yellow-200',
      iconColor: 'text-yellow-500',
      tooltip: 'Normalização aguardando processamento',
    },
    processing: {
      icon: ClockIcon,
      label: 'Normalizando',
      color: 'bg-blue-50 text-blue-700 border-blue-200',
      iconColor: 'text-blue-500',
      tooltip: 'Normalização em andamento',
      animate: true,
    },
    completed: {
      icon: CheckCircleIcon,
      label: 'Normalizado',
      color: 'bg-green-50 text-green-700 border-green-200',
      iconColor: 'text-green-500',
      tooltip: 'Dados normalizados com sucesso',
    },
    failed: {
      icon: ExclamationTriangleIcon,
      label: 'Falha',
      color: 'bg-red-50 text-red-700 border-red-200',
      iconColor: 'text-red-500',
      tooltip: error || 'Erro ao normalizar dados',
    },
    skipped: {
      icon: MinusCircleIcon,
      label: 'Sem dados',
      color: 'bg-gray-50 text-gray-600 border-gray-200',
      iconColor: 'text-gray-400',
      tooltip: 'Sem dados para normalizar',
    },
  };

  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <div
      className={`inline-flex items-center gap-1 rounded-full border ${padding} ${config.color} ${textSize}`}
      title={config.tooltip}
    >
      <Icon
        className={`${iconSize} ${config.iconColor} ${config.animate ? 'animate-spin' : ''}`}
      />
      {showLabel && <span className="font-medium">{config.label}</span>}
    </div>
  );
};
