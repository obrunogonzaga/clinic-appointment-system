import {
    CalendarDaysIcon,
    HomeIcon,
    TruckIcon,
    UserIcon,
    ArrowLeftOnRectangleIcon,
    ShieldCheckIcon,
} from '@heroicons/react/24/outline';
import React from 'react';
import { useAuth } from '../hooks/useAuth';

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

export const Navigation: React.FC<NavigationProps> = ({ activeTab, onTabChange }) => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    if (window.confirm('Tem certeza que deseja sair?')) {
      try {
        await logout();
      } catch (error) {
        console.error('Logout error:', error);
        // Force redirect even if API call fails
        window.location.href = '/login';
      }
    }
  };

  return (
    <nav className="bg-white shadow-sm border-r border-gray-200 w-64 min-h-screen flex flex-col">
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

      {/* User info and logout at bottom */}
      <div className="mt-auto p-6 border-t border-gray-200">
        {user && (
          <div className="mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <UserIcon className="w-4 h-4 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  Olá, {user.name.split(' ')[0]}!
                </p>
                <div className="flex items-center space-x-1">
                  <p className="text-xs text-gray-500 truncate">
                    {user.email}
                  </p>
                  {user.is_admin && (
                    <ShieldCheckIcon className="w-3 h-3 text-green-500" title="Administrador" />
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
        
        <button
          onClick={handleLogout}
          className="w-full flex items-center space-x-3 px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors duration-200"
        >
          <ArrowLeftOnRectangleIcon className="w-5 h-5 text-gray-400" />
          <span className="text-sm font-medium">Sair</span>
        </button>
      </div>
    </nav>
  );
};