import {
  ArrowLeftOnRectangleIcon,
  CalendarDaysIcon,
  ChartBarIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  HomeIcon,
  MoonIcon,
  Squares2X2Icon,
  SunIcon,
  TagIcon,
  TruckIcon,
  UserGroupIcon,
  UserIcon,
} from '@heroicons/react/24/outline';
import type { ComponentType, ReactNode } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Role, ROLE_LABELS } from '../constants/roles';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from '../hooks/useTheme';

interface NavigationItem {
  id: string;
  name: string;
  description: string;
  icon: ComponentType<{ className?: string }>;
  to: string;
  allowedRoles: Role[];
}

interface NavigationGroup {
  id: string;
  label: string;
  icon?: ReactNode;
  allowedRoles: Role[];
  items: NavigationItem[];
}

interface NavigationProps {
  role: Role | null;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const NAVIGATION_GROUPS: NavigationGroup[] = [
  {
    id: 'operation',
    label: 'Operação',
    icon: <ChartBarIcon className="w-4 h-4" aria-hidden="true" />,
    allowedRoles: [Role.COLABORADOR, Role.ADMIN],
    items: [
      {
        id: 'dashboard',
        name: 'Dashboard',
        description: 'Visão geral do seu dia',
        icon: HomeIcon,
        to: '/dashboard',
        allowedRoles: [Role.COLABORADOR, Role.ADMIN],
      },
      {
        id: 'appointments',
        name: 'Agendamentos',
        description: 'Gerenciar agendamentos',
        icon: CalendarDaysIcon,
        to: '/agendamentos',
        allowedRoles: [Role.COLABORADOR, Role.ADMIN],
      },
    ],
  },
  {
    id: 'registrations',
    label: 'Cadastros',
    icon: <Squares2X2Icon className="w-4 h-4" aria-hidden="true" />,
    allowedRoles: [Role.COLABORADOR, Role.ADMIN],
    items: [
      {
        id: 'drivers',
        name: 'Motoristas',
        description: 'Cadastro e acompanhamento de motoristas',
        icon: TruckIcon,
        to: '/cadastros/motoristas',
        allowedRoles: [Role.COLABORADOR, Role.ADMIN],
      },
      {
        id: 'collectors',
        name: 'Coletoras',
        description: 'Gerencie a equipe de coleta',
        icon: UserGroupIcon,
        to: '/cadastros/coletoras',
        allowedRoles: [Role.COLABORADOR, Role.ADMIN],
      },
      {
        id: 'cars',
        name: 'Carros',
        description: 'Frota disponível e manutenção',
        icon: TruckIcon,
        to: '/cadastros/carros',
        allowedRoles: [Role.COLABORADOR, Role.ADMIN],
      },
      {
        id: 'packages',
        name: 'Pacotes',
        description: 'Combinações de recursos',
        icon: Squares2X2Icon,
        to: '/cadastros/pacotes',
        allowedRoles: [Role.COLABORADOR, Role.ADMIN],
      },
    ],
  },
  {
    id: 'administration',
    label: 'Administração',
    icon: <UserIcon className="w-4 h-4" aria-hidden="true" />,
    allowedRoles: [Role.ADMIN],
    items: [
      {
        id: 'users',
        name: 'Usuários',
        description: 'Gestão de perfis e convites',
        icon: UserIcon,
        to: '/admin/usuarios',
        allowedRoles: [Role.ADMIN],
      },
      {
        id: 'tags',
        name: 'Tags',
        description: 'Organize os agendamentos com tags',
        icon: TagIcon,
        to: '/admin/tags',
        allowedRoles: [Role.ADMIN],
      },
    ],
  },
];

const buildInitialGroupState = (groups: NavigationGroup[]): Record<string, boolean> => {
  return groups.reduce<Record<string, boolean>>((accumulator, group) => {
    accumulator[group.id] = true;
    return accumulator;
  }, {});
};

export const Navigation: React.FC<NavigationProps> = ({
  role,
  isCollapsed,
  onToggleCollapse,
}) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const visibleGroups = useMemo(() => {
    return NAVIGATION_GROUPS.map((group) => ({
      ...group,
      items: group.items.filter((item) =>
        role ? item.allowedRoles.includes(role) : item.allowedRoles.includes(Role.COLABORADOR)
      ),
    }))
      .filter((group) =>
        role ? group.allowedRoles.includes(role) && group.items.length > 0 : group.items.length > 0
      );
  }, [role]);

  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(() =>
    buildInitialGroupState(visibleGroups)
  );

  useEffect(() => {
    setExpandedGroups((previous) => {
      const next = buildInitialGroupState(visibleGroups);
      return {
        ...next,
        ...previous,
      };
    });
  }, [visibleGroups]);

  useEffect(() => {
    if (isCollapsed) {
      setExpandedGroups((previous) => {
        const nextState: Record<string, boolean> = {};
        Object.keys(previous).forEach((key) => {
          nextState[key] = false;
        });
        return nextState;
      });
    }
  }, [isCollapsed]);

  const handleGroupToggle = useCallback((groupId: string) => {
    setExpandedGroups((previous) => ({
      ...previous,
      [groupId]: !previous[groupId],
    }));
  }, []);

  const handleLogout = useCallback(async () => {
    if (!window.confirm('Tem certeza que deseja sair?')) {
      return;
    }

    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
      window.location.href = '/login';
    }
  }, [logout]);

  return (
    <nav
      className={`bg-white dark:bg-slate-950 shadow-sm border-r border-gray-200/80 dark:border-slate-800 min-h-screen flex flex-col transition-all duration-300 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
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
            <ChevronDownIcon className="w-5 h-5 rotate-90" aria-hidden="true" />
          ) : (
            <ChevronDownIcon className="w-5 h-5 -rotate-90" aria-hidden="true" />
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
            <SunIcon className="h-5 w-5" aria-hidden="true" />
          ) : (
            <MoonIcon className="h-5 w-5" aria-hidden="true" />
          )}
          {!isCollapsed && (
            <span className="text-sm font-medium">
              {theme === 'dark' ? 'Modo claro' : 'Modo escuro'}
            </span>
          )}
        </button>
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'space-x-2'}`}>
          <UserIcon className={`text-blue-600 dark:text-blue-400 ${isCollapsed ? 'w-7 h-7' : 'w-8 h-8'}`} aria-hidden="true" />
          {!isCollapsed && (
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-slate-100">Sistema de Agendamentos</h1>
              {role && (
                <p className="text-xs text-gray-500 dark:text-slate-400">
                  Perfil: {ROLE_LABELS[role]}
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      <div className={`flex-1 overflow-y-auto ${isCollapsed ? 'px-2' : 'px-4'} py-4 space-y-2`}>
        {visibleGroups.length === 0 ? (
          <div className="text-xs text-gray-500 dark:text-slate-400 text-center px-2">
            Carregando navegação...
          </div>
        ) : (
          visibleGroups.map((group) => {
            const isGroupExpanded = expandedGroups[group.id];

            if (isCollapsed) {
              return (
                <div key={group.id} className="flex flex-col gap-2">
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    const isActive =
                      location.pathname === item.to ||
                      location.pathname.startsWith(`${item.to}/`);
                    return (
                      <NavLink
                        key={item.id}
                        to={item.to}
                        className={`w-full flex items-center justify-center p-3 rounded-lg transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                          isActive
                            ? 'bg-blue-50 dark:bg-blue-500/20 text-blue-700 dark:text-blue-200'
                            : 'text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-900'
                        }`}
                        aria-label={item.name}
                        title={item.name}
                      >
                        <Icon
                          className={`w-5 h-5 ${
                            isActive
                              ? 'text-blue-600 dark:text-blue-200'
                              : 'text-gray-400 dark:text-slate-500'
                          }`}
                          aria-hidden="true"
                        />
                      </NavLink>
                    );
                  })}
                </div>
              );
            }

            return (
              <section key={group.id} aria-label={group.label} className="space-y-1">
                <button
                  type="button"
                  onClick={() => handleGroupToggle(group.id)}
                  className="w-full flex items-center justify-between px-2 py-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-slate-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
                  aria-expanded={isGroupExpanded}
                >
                  <span className="flex items-center gap-2">
                    {group.icon}
                    {group.label}
                  </span>
                  {isGroupExpanded ? (
                    <ChevronUpIcon className="w-4 h-4" aria-hidden="true" />
                  ) : (
                    <ChevronDownIcon className="w-4 h-4" aria-hidden="true" />
                  )}
                </button>
                {isGroupExpanded && (
                  <div className="space-y-1">
                    {group.items.map((item) => {
                      const Icon = item.icon;
                      const isActive =
                        location.pathname === item.to ||
                        location.pathname.startsWith(`${item.to}/`);
                      return (
                        <NavLink
                          key={item.id}
                          to={item.to}
                          className={`w-full flex items-center px-3 py-3 rounded-lg transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
                            isActive
                              ? 'bg-blue-50 dark:bg-blue-500/20 text-blue-700 dark:text-blue-200 border-l-4 border-blue-600 dark:border-blue-400'
                              : 'text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-900'
                          }`}
                        >
                          <Icon
                            className={`w-5 h-5 flex-shrink-0 ${
                              isActive
                                ? 'text-blue-600 dark:text-blue-200'
                                : 'text-gray-400 dark:text-slate-500'
                            }`}
                            aria-hidden="true"
                          />
                          <div className="ml-3 text-left">
                            <p
                              className={`font-medium ${
                                isActive
                                  ? 'text-blue-900 dark:text-blue-100'
                                  : 'text-gray-900 dark:text-slate-100'
                              }`}
                            >
                              {item.name}
                            </p>
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
                        </NavLink>
                      );
                    })}
                  </div>
                )}
              </section>
            );
          })
        )}
      </div>

      <div className={`mt-auto border-t border-gray-200 dark:border-slate-800 ${isCollapsed ? 'px-2 py-4' : 'px-6 py-6'}`}>
        {!isCollapsed && user && (
          <div className="mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-500/20 rounded-full flex items-center justify-center">
                <UserIcon className="w-5 h-5 text-blue-600 dark:text-blue-300" aria-hidden="true" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">
                  Olá, {user.name.split(' ')[0]}!
                </p>
                <div className="flex items-center space-x-1">
                  <p className="text-xs text-gray-500 dark:text-slate-400 truncate">{user.email}</p>
                  {role === Role.ADMIN && (
                    <span className="text-[10px] font-semibold text-green-600 uppercase tracking-wide">
                      Admin
                    </span>
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
          <ArrowLeftOnRectangleIcon className="w-5 h-5 text-gray-400 dark:text-slate-500" aria-hidden="true" />
          {!isCollapsed && <span className="text-sm font-medium">Sair</span>}
        </button>
      </div>
    </nav>
  );
};

