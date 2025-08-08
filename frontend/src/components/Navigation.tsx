import React from 'react';
import {
  HomeIcon,
  UserIcon,
  CalendarDaysIcon,
  TruckIcon,
} from '@heroicons/react/24/outline';

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
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
];

export const Navigation: React.FC<NavigationProps> = ({ activeTab, onTabChange }) => {
  return (
    <nav className="bg-white shadow-sm border-r border-gray-200 w-64 min-h-screen">
      <div className="p-6">
        <div className="flex items-center space-x-2 mb-8">
          <UserIcon className="w-8 h-8 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900">
            Sistema de Agendamentos
          </h1>
        </div>

        <div className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors duration-200 ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-blue-600' : 'text-gray-400'}`} />
                <div>
                  <p className={`font-medium ${isActive ? 'text-blue-900' : 'text-gray-900'}`}>
                    {item.name}
                  </p>
                  <p className={`text-xs ${isActive ? 'text-blue-600' : 'text-gray-500'}`}>
                    {item.description}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};