import {
    CalendarIcon,
    QueueListIcon,
    Squares2X2Icon,
    TableCellsIcon,
} from '@heroicons/react/24/outline';
import React from 'react';

export type ViewMode = 'cards' | 'table' | 'calendar' | 'agenda';

interface ViewModeToggleProps {
  viewMode: ViewMode;
  onViewChange: (mode: ViewMode) => void;
  className?: string;
  variant?: 'default' | 'minimal';
}

interface ViewOption {
  mode: ViewMode;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

const viewOptions: ViewOption[] = [
  {
    mode: 'cards',
    label: 'Cards',
    icon: Squares2X2Icon,
    description: 'Visualização em cards'
  },
  {
    mode: 'table',
    label: 'Lista',
    icon: TableCellsIcon,
    description: 'Visualização em tabela'
  },
  {
    mode: 'calendar',
    label: 'Calendário',
    icon: CalendarIcon,
    description: 'Visualização em calendário'
  },
  {
    mode: 'agenda',
    label: 'Agenda',
    icon: QueueListIcon,
    description: 'Agenda das coletoras'
  }
];

export const ViewModeToggle: React.FC<ViewModeToggleProps> = ({
  viewMode,
  onViewChange,
  className = '',
  variant = 'default',
}) => {
  const baseContainerClass = variant === 'minimal'
    ? 'flex rounded-full'
    : 'flex rounded-lg bg-gray-100 p-1';

  return (
    <div className={`${baseContainerClass} ${className}`}>
      {viewOptions.map(({ mode, label, icon: Icon, description }) => (
        <button
          key={mode}
          onClick={() => onViewChange(mode)}
          title={description}
          aria-pressed={viewMode === mode}
          className={`
            flex items-center rounded-full px-3 py-2 text-sm font-medium transition-all duration-200
            ${viewMode === mode 
              ? 'bg-white text-gray-900 shadow-sm ring-1 ring-gray-200' 
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }
          `}
        >
          {variant === 'default' && <Icon className="mr-2 h-4 w-4" />}
          <span>{label}</span>
        </button>
      ))}
    </div>
  );
};
