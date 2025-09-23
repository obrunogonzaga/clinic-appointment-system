import {
  ArrowLeftOnRectangleIcon,
  CalendarDaysIcon,
  ChevronDoubleLeftIcon,
  ChevronDoubleRightIcon,
  HomeIcon,
  MoonIcon,
  ShieldCheckIcon,
  SunIcon,
  TruckIcon,
  UserIcon,
} from '@heroicons/react/24/outline';
import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from '../hooks/useTheme';

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
    adminOnly: false,
  },
  {
    id: 'appointments',
    name: 'Agendamentos',
    icon: CalendarDaysIcon,
    description: 'Gerenciar agendamentos',
    adminOnly: false,
  },
  {
    id: 'drivers',
    name: 'Motoristas',
    icon: TruckIcon,
    description: 'Cadastrar e gerenciar motoristas',
    adminOnly: false,
  },
  {
    id: 'collectors',
    name: 'Coletoras',
    icon: UserIcon,
    description: 'Cadastrar e gerenciar coletoras',
    adminOnly: false,
  },
  {
    id: 'cars',
    name: 'Carros',
    icon: TruckIcon,
    description: 'Cadastrar e gerenciar carros',
    adminOnly: false,
  },
  {
    id: 'users',
    name: 'Usuários',
    icon: UserIcon,
    description: 'Gerenciar usuários do sistema',
    adminOnly: true,
  },
];

export const Navigation: React.FC<NavigationProps> = ({
  activeTab,
  onTabChange,
  isCollapsed,
  onToggleCollapse,
}) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const handleLogout = async () => {
    if (!window.confirm('Tem certeza que deseja sair?')) {
      return;
    }

    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
      window.location.href = '/login';
    }
  };

  const visibleNavigationItems = navigationItems.filter(
    (item) => !item.adminOnly || user?.is_admin,
  );

  return (
    <nav
      className={`bg-white dark:bg-slate-950 shadow-sm border-r border-gray-200/80 dark:border-slate-800 min-h-screen flex flex-col transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div
        className={`border-b border-gray-100 dark:border-slate-800 flex flex-col gap-6 ${
          isCollapsed ? 'px-2 py-4' : 'px-6 py-6'
        }`}
      >
        <button
          type="button"
          onClick={onToggleCollapse}
          className="self-end p-2 text-gray-500 dark:text-slate-400 hover:text-gray-700 hover:bg-gray-100 dark:hover:text-slate-200 dark:hover:bg-slate-900 rounded-md transition-colors"
          aria-label={isCollapsed ? 'Expandir menu lateral' : 'Recolher menu lateral'}
          aria-expanded={!isCollapsed}
        >
          {isCollapsed ? (
            <ChevronDoubleRightIcon className="w-5 h-5" />
          ) : (
            <ChevronDoubleLeftIcon className="w-5 h-5" />
          )}
        </button>
        <button
          type="button"
          onClick={toggleTheme}
          className={`inline-flex items-center justify-center rounded-md border border-transparent bg-gray-100 dark:bg-slate-900 text-gray-600 dark:text-slate-300 hover:bg-gray-200 dark:hover:bg-slate-800 transition-colors ${
            isCollapsed ? 'mx-auto h-9 w-9' : 'w-full px-4 py-2 gap-2'
          }`}
          aria-label={theme === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro'}
          title={theme === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro'}
        >
          {theme === 'dark' ? (
            <SunIcon className="h-5 w-5" />
          ) : (
            <MoonIcon className="h-5 w-5" />
          )}
          {!isCollapsed && (
            <span className="text-sm font-medium">
              {theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
            </span>
          )}
        </button>
        <div
          className={`flex items-center ${
            isCollapsed ? 'justify-center' : 'space-x-2'
          }`}
        >
          <UserIcon
            className={`text-blue-600 dark:text-blue-400 ${isCollapsed ? 'w-7 h-7' : 'w-8 h-8'}`}
          />
          {!isCollapsed && (
            <h1 className="text-xl font-bold text-gray-900 dark:text-slate-100">
              Sistema de Agendamentos
            </h1>
          )}
        </div>
      </div>

      <div className={`flex-1 ${isCollapsed ? 'px-2' : 'px-4'} py-4 space-y-2`}>
        {visibleNavigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const buttonClasses = `w-full flex items-center px-3 py-3 rounded-lg transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
            isCollapsed ? 'justify-center' : 'space-x-3 text-left'
          } ${
            isActive
              ? `bg-blue-50 dark:bg-blue-500/20 text-blue-700 dark:text-blue-200 ${
                  isCollapsed ? '' : 'border-l-4 border-blue-600 dark:border-blue-400'
                }`
              : 'text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-900'
          }`;

          return (
            <button
              type="button"
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={buttonClasses}
              aria-label={item.name}
            >
              <Icon
                className={`w-5 h-5 ${
                  isActive
                    ? 'text-blue-600 dark:text-blue-300'
                    : 'text-gray-400 dark:text-slate-500'
                }`}
              />
              {!isCollapsed && (
                <div>
                  <div className="flex items-center">
                    <p
                      className={`font-medium ${
                        isActive
                          ? 'text-blue-900 dark:text-blue-100'
                          : 'text-gray-900 dark:text-slate-100'
                      }`}
                    >
                      {item.name}
                    </p>
                    {item.adminOnly && (
                      <ShieldCheckIcon
                        className="w-3 h-3 text-green-500 ml-1"
                        title="Apenas Admin"
                      />
                    )}
                  </div>
                  <p
                    className={`text-xs ${
                      isActive
                        ? 'text-blue-600 dark:text-blue-200'
                        : 'text-gray-500 dark:text-slate-400'
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

      <div
        className={`mt-auto border-t border-gray-200 dark:border-slate-800 ${
          isCollapsed ? 'px-2 py-4' : 'px-6 py-6'
        }`}
      >
        {!isCollapsed && user && (
          <div className="mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-500/20 rounded-full flex items-center justify-center">
                <UserIcon className="w-4 h-4 text-blue-600 dark:text-blue-300" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
                  Olá, {user.name.split(' ')[0]}!
                </p>
                <div className="flex items-center space-x-1">
                  <p className="text-xs text-gray-500 dark:text-slate-400 truncate">{user.email}</p>
                  {user.is_admin && (
                    <ShieldCheckIcon
                      className="w-3 h-3 text-green-500"
                      title="Administrador"
                    />
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        <button
          type="button"
          onClick={handleLogout}
          className={`w-full flex items-center rounded-lg text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-900 transition-colors duration-200 ${
            isCollapsed ? 'justify-center p-2' : 'space-x-3 px-4 py-2'
          }`}
          aria-label="Sair"
        >
          <ArrowLeftOnRectangleIcon className="w-5 h-5 text-gray-400 dark:text-slate-500" />
          {!isCollapsed && <span className="text-sm font-medium">Sair</span>}
        </button>
      </div>
    </nav>
  );
};
