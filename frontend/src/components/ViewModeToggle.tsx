import {
    CalendarIcon,
    QueueListIcon,
    Squares2X2Icon,
} from '@heroicons/react/24/outline';
import React from 'react';

export type ViewMode = 'cards' | 'calendar' | 'agenda';

interface ViewModeToggleProps {
  viewMode: ViewMode;
  onViewChange: (mode: ViewMode) => void;
  className?: string;
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
  className = ''
}) => {
  return (
    <div className={`flex bg-gray-100 rounded-lg p-1 ${className}`}>
      {viewOptions.map(({ mode, label, icon: Icon, description }) => (
        <button
          key={mode}
          onClick={() => onViewChange(mode)}
          title={description}
          className={`
            flex items-center px-3 py-2 rounded-md text-sm font-medium transition-all duration-200
            ${viewMode === mode 
              ? 'bg-white text-gray-900 shadow-sm ring-1 ring-gray-200' 
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }
          `}
        >
          <Icon className="w-4 h-4" />
          <span className="ml-2 hidden sm:inline">{label}</span>
        </button>
      ))}
    </div>
  );
};
