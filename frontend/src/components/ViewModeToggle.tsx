import React from 'react';
import {
  ListBulletIcon,
  Squares2X2Icon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import { useResponsiveLayout } from '../hooks/useResponsiveLayout';

export type ViewMode = 'table' | 'cards' | 'calendar';

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
    mode: 'table',
    label: 'Tabela',
    icon: ListBulletIcon,
    description: 'Visualização em tabela'
  },
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
  }
];

export const ViewModeToggle: React.FC<ViewModeToggleProps> = ({
  viewMode,
  onViewChange,
  className = ''
}) => {
  const { isMobile } = useResponsiveLayout();
  
  // Filter out table mode on mobile devices
  const availableOptions = viewOptions.filter(option => 
    !isMobile || option.mode !== 'table'
  );

  return (
    <div className={`flex bg-gray-100 rounded-lg p-1 ${className}`}>
      {availableOptions.map(({ mode, label, icon: Icon, description }) => (
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
