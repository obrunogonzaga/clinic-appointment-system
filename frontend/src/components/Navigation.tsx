import {
  CalendarDaysIcon,
  ChevronDoubleLeftIcon,
  ChevronDoubleRightIcon,
  HomeIcon,
  TruckIcon,
  UserIcon,
} from '@heroicons/react/24/outline';
import React from 'react';

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const navigationItems = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    icon: HomeIcon,
    description: 'Visão geral e upload de arquivos',
  },
  {
    id: 'appointments',
    name: 'Agendamentos',
    icon: CalendarDaysIcon,
    description: 'Gerenciar agendamentos',
  },
  {
    id: 'drivers',
    name: 'Motoristas',
    icon: TruckIcon,
    description: 'Cadastrar e gerenciar motoristas',
  },
  {
    id: 'collectors',
    name: 'Coletoras',
    icon: UserIcon,
    description: 'Cadastrar e gerenciar coletoras',
  },
  {
    id: 'cars',
    name: 'Carros',
    icon: TruckIcon,
    description: 'Cadastrar e gerenciar carros',
  },
];

export const Navigation: React.FC<NavigationProps> = ({
  activeTab,
  onTabChange,
  isCollapsed,
  onToggleCollapse,
}) => {
  return (
    <nav
      className={`bg-white shadow-sm border-r border-gray-200 min-h-screen flex flex-col transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div
        className={`border-b border-gray-100 flex flex-col gap-6 ${
          isCollapsed ? 'px-2 py-4' : 'px-6 py-6'
        }`}
      >
        <button
          type="button"
          onClick={onToggleCollapse}
          className="self-end p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
          aria-label={isCollapsed ? 'Expandir menu lateral' : 'Recolher menu lateral'}
          aria-expanded={!isCollapsed}
        >
          {isCollapsed ? (
            <ChevronDoubleRightIcon className="w-5 h-5" />
          ) : (
            <ChevronDoubleLeftIcon className="w-5 h-5" />
          )}
        </button>
        <div
          className={`flex items-center ${
            isCollapsed ? 'justify-center' : 'space-x-2'
          }`}
        >
          <UserIcon
            className={`text-blue-600 ${isCollapsed ? 'w-7 h-7' : 'w-8 h-8'}`}
          />
          {!isCollapsed && (
            <h1 className="text-xl font-bold text-gray-900">
              Sistema de Agendamentos
            </h1>
          )}
        </div>
      </div>

      <div className={`flex-1 ${isCollapsed ? 'px-2' : 'px-4'} py-4 space-y-2`}>
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const buttonClasses = `w-full flex items-center px-3 py-3 rounded-lg transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
            isCollapsed ? 'justify-center' : 'space-x-3 text-left'
          } ${
            isActive
              ? `bg-blue-50 text-blue-700 ${
                  isCollapsed ? '' : 'border-l-4 border-blue-600'
                }`
              : 'text-gray-700 hover:bg-gray-50'
          }`;

          return (
            <button
              type="button"
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={buttonClasses}
            >
              <Icon
                className={`w-5 h-5 ${isActive ? 'text-blue-600' : 'text-gray-400'}`}
              />
              {!isCollapsed && (
                <div>
                  <p
                    className={`font-medium ${
                      isActive ? 'text-blue-900' : 'text-gray-900'
                    }`}
                  >
                    {item.name}
                  </p>
                  <p
                    className={`text-xs ${
                      isActive ? 'text-blue-600' : 'text-gray-500'
                    }`}
                  >
                    {item.description}
                  </p>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};