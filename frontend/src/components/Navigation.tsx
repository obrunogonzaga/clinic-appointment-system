import {
  ArrowLeftOnRectangleIcon,
  CalendarDaysIcon,
  ChevronDoubleLeftIcon,
  ChevronDoubleRightIcon,
  ClipboardDocumentListIcon,
  HomeIcon,
  MoonIcon,
  Squares2X2Icon,
  SunIcon,
  TagIcon,
  TruckIcon,
  UserCircleIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';
import React, { useEffect, useMemo, useState } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import type { Role } from '../constants/roles';
import { ROLES } from '../constants/roles';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from '../hooks/useTheme';
import { getUserRole } from '../utils/session';

interface NavigationItem {
  id: string;
  label: string;
  description: string;
  to: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  allowedRoles?: Role[];
}

interface NavigationGroup {
  id: string;
  title: string;
  items: NavigationItem[];
  allowedRoles?: Role[];
}

interface NavigationProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const navigationGroups: NavigationGroup[] = [
  {
    id: 'operacao',
    title: 'Operação',
    items: [
      {
        id: 'dashboard',
        label: 'Dashboard',
        description: 'Resumo focado em operação',
        to: '/dashboard',
        icon: HomeIcon,
      },
      {
        id: 'agendamentos',
        label: 'Agendamentos',
        description: 'Gerenciar agendamentos e calendário',
        to: '/agendamentos',
        icon: CalendarDaysIcon,
      },
    ],
  },
  {
    id: 'cadastros',
    title: 'Cadastros',
    items: [
      {
        id: 'motoristas',
        label: 'Motoristas',
        description: 'Cadastrar e gerenciar motoristas',
        to: '/cadastros/motoristas',
        icon: TruckIcon,
      },
      {
        id: 'coletoras',
        label: 'Coletoras',
        description: 'Gerenciar equipe de coleta',
        to: '/cadastros/coletoras',
        icon: UserGroupIcon,
      },
      {
        id: 'carros',
        label: 'Carros',
        description: 'Frota disponível para agendamentos',
        to: '/cadastros/carros',
        icon: TruckIcon,
      },
      {
        id: 'pacotes',
        label: 'Pacotes',
        description: 'Combinações prontas de recursos',
        to: '/cadastros/pacotes',
        icon: Squares2X2Icon,
      },
    ],
  },
  {
    id: 'administracao',
    title: 'Administração',
    allowedRoles: [ROLES.ADMIN],
    items: [
      {
        id: 'usuarios',
        label: 'Usuários',
        description: 'Gerenciar usuários do sistema',
        to: '/admin/usuarios',
        icon: UserCircleIcon,
        allowedRoles: [ROLES.ADMIN],
      },
      {
        id: 'tags',
        label: 'Tags',
        description: 'Organizar tags de agendamento',
        to: '/admin/tags',
        icon: TagIcon,
        allowedRoles: [ROLES.ADMIN],
      },
    ],
  },
];

const buildInitialGroupState = (pathname: string) => {
  const state: Record<string, boolean> = {};
  navigationGroups.forEach((group) => {
    state[group.id] = pathname.startsWith(`/${group.id}`) || pathname.startsWith('/dashboard')
      ? true
      : group.id !== 'administracao';
  });
  return state;
};

export const Navigation: React.FC<NavigationProps> = ({
  isCollapsed,
  onToggleCollapse,
}) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>(() =>
    buildInitialGroupState(location.pathname),
  );

  useEffect(() => {
    setOpenGroups((previous) => {
      const next = { ...previous };
      navigationGroups.forEach((group) => {
        const shouldBeOpen = group.items.some((item) =>
          location.pathname.startsWith(item.to),
        );
        if (shouldBeOpen) {
          next[group.id] = true;
        }
      });
      return next;
    });
  }, [location.pathname]);

  const handleLogout = async () => {
    if (!window.confirm('Tem certeza que deseja sair?')) {
      return;
    }

    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/login');
    }
  };

  const userRole = useMemo(() => getUserRole(user), [user]);

  const visibleGroups = useMemo(() => {
    return navigationGroups
      .map<NavigationGroup | null>((group) => {
        if (group.allowedRoles && !group.allowedRoles.includes(userRole)) {
          return null;
        }

        const filteredItems = group.items.filter((item) =>
          item.allowedRoles ? item.allowedRoles.includes(userRole) : true,
        );

        if (filteredItems.length === 0) {
          return null;
        }

        return {
          ...group,
          items: filteredItems,
        };
      })
      .filter(Boolean) as NavigationGroup[];
  }, [userRole]);

  const renderNavigationItem = (item: NavigationItem) => {
    const Icon = item.icon;
    return (
      <NavLink
        key={item.id}
        to={item.to}
        end={item.to === '/dashboard'}
        className={({ isActive }) =>
          [
            'group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all duration-200',
            isActive
              ? 'bg-blue-100 text-blue-700 dark:bg-slate-900 dark:text-blue-300'
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-white',
            isCollapsed ? 'justify-center' : 'justify-start',
          ].join(' ')
        }
        aria-label={item.label}
      >
        <Icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
        {!isCollapsed && (
          <div className="flex flex-col text-left">
            <span className="font-semibold leading-5">{item.label}</span>
            <span className="text-xs text-gray-500 dark:text-slate-400 leading-4">
              {item.description}
            </span>
          </div>
        )}
      </NavLink>
    );
  };

  return (
    <nav
      className={`bg-white dark:bg-slate-950 shadow-sm border-r border-gray-200/80 dark:border-slate-800 min-h-screen flex flex-col transition-all duration-300 ${
        isCollapsed ? 'w-20' : 'w-72'
      }`}
      aria-label="Menu principal"
    >
      <div className={`border-b border-gray-100 dark:border-slate-800 flex flex-col gap-6 ${isCollapsed ? 'px-2 py-4' : 'px-6 py-6'}`}>
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
            isCollapsed ? 'mx-auto h-10 w-10' : 'w-full px-4 py-2 gap-2'
          }`}
          aria-label={theme === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro'}
          title={theme === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro'}
        >
          {theme === 'dark' ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
          {!isCollapsed && <span className="text-sm font-medium">{theme === 'dark' ? 'Modo claro' : 'Modo escuro'}</span>}
        </button>
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'space-x-3'}`}>
          <UserCircleIcon className="h-10 w-10 text-blue-600" aria-hidden="true" />
          {!isCollapsed && (
            <div className="min-w-0">
              <p className="text-sm font-semibold text-gray-900 dark:text-white truncate" aria-live="polite">
                {user?.name ?? 'Usuário'}
              </p>
              <p className="text-xs text-gray-500 dark:text-slate-400 truncate">
                {user?.email ?? 'sem-email@widia.app'}
              </p>
              <p className="mt-1 text-xs uppercase tracking-wide text-blue-600 dark:text-blue-400 font-semibold">
                {userRole === ROLES.ADMIN ? 'Administrador' : 'Colaborador'}
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-4" role="menubar">
        {visibleGroups.map((group) => {
          const isGroupOpen = openGroups[group.id];
          return (
            <div key={group.id} className="space-y-2">
              <button
                type="button"
                onClick={() =>
                  setOpenGroups((previous) => ({
                    ...previous,
                    [group.id]: !previous[group.id],
                  }))
                }
                className={`w-full flex items-center justify-between text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400 ${
                  isCollapsed ? 'px-1' : 'px-2'
                }`}
                aria-expanded={isGroupOpen}
                aria-controls={`group-${group.id}`}
              >
                <span>{group.title}</span>
                {!isCollapsed && (
                  <ClipboardDocumentListIcon
                    className={`h-4 w-4 transition-transform ${isGroupOpen ? 'rotate-0' : '-rotate-90'}`}
                    aria-hidden="true"
                  />
                )}
              </button>
              <div
                id={`group-${group.id}`}
                className={`${isGroupOpen ? 'space-y-2' : 'hidden'} ${isCollapsed ? '' : 'pl-1'}`}
                role="menu"
              >
                {group.items.map((item) => renderNavigationItem(item))}
              </div>
            </div>
          );
        })}
      </div>

      <div className={`border-t border-gray-200 dark:border-slate-800 ${isCollapsed ? 'px-2 py-4' : 'px-6 py-6'}`}>
        <button
          type="button"
          onClick={handleLogout}
          className={`w-full inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-semibold text-red-600 hover:bg-red-50 dark:hover:bg-slate-900 transition-colors ${
            isCollapsed ? 'flex-col text-center' : 'flex-row'
          }`}
        >
          <ArrowLeftOnRectangleIcon className="h-5 w-5" aria-hidden="true" />
          <span>Sair</span>
        </button>
      </div>
    </nav>
  );
};
