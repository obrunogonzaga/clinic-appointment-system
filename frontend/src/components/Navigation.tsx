import {
  ArrowLeftOnRectangleIcon,
  ChevronDoubleLeftIcon,
  ChevronDoubleRightIcon,
  MoonIcon,
  SunIcon,
} from '@heroicons/react/24/outline';
import React, { useMemo, useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  NAVIGATION_GROUP_LABELS,
  type NavigationGroupId,
  type NavigationItem,
  getNavigationItemsByRole,
} from '../config/navigationConfig';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from '../hooks/useTheme';
import { resolveUserRole } from '../utils/session';
import sergioFrancoLogo from '../assets/sergio-franco-logo.svg';
import sergioFrancoMark from '../assets/sergio-franco-mark.svg';

interface NavigationProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  isCollapsed,
  onToggleCollapse,
}) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const role = resolveUserRole(user);

  const groupedItems = useMemo(() => {
    const itemsByRole = getNavigationItemsByRole(role);

    const map = new Map<NavigationGroupId, NavigationItem[]>([
      ['operacao', []],
      ['cadastros', []],
      ['administracao', []],
    ]);

    itemsByRole.forEach((item) => {
      const list = map.get(item.group);
      if (list) {
        list.push(item);
      }
    });

    return map;
  }, [role]);

  const [collapsedGroups, setCollapsedGroups] = useState<Record<NavigationGroupId, boolean>>({
    operacao: false,
    cadastros: false,
    administracao: false,
  });

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

  const toggleGroup = (group: NavigationGroupId) => {
    setCollapsedGroups((previous) => ({
      ...previous,
      [group]: !previous[group],
    }));
  };

  const renderNavLink = (item: NavigationItem) => {
    const Icon = item.icon;
    const fallbackActive = (() => {
      const matchPaths = item.matchPaths ?? [item.to];
      return matchPaths.some((path) => location.pathname.startsWith(path));
    })();

    return (
      <NavLink
        key={item.id}
        to={item.to}
        className={({ isActive: linkActive }) => {
          const active = linkActive || fallbackActive;
          return [
            'w-full flex items-center rounded-lg transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 px-3 py-3',
            isCollapsed ? 'justify-center' : 'gap-3 text-left',
            active
              ? 'bg-blue-50 dark:bg-blue-500/20 text-blue-700 dark:text-blue-200'
              : 'text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-900',
            !isCollapsed && active ? 'border-l-4 border-blue-600 dark:border-blue-400 pl-1' : '',
          ]
            .filter(Boolean)
            .join(' ');
        }}
      >
        {({ isActive: linkActive }) => {
          const active = linkActive || fallbackActive;
          return (
            <>
              <Icon
                className={`h-5 w-5 ${
                  active ? 'text-blue-600 dark:text-blue-300' : 'text-gray-400 dark:text-slate-500'
                }`}
                aria-hidden="true"
              />
              {!isCollapsed && (
                <div className="flex flex-col">
                  <span className="text-sm font-semibold">{item.label}</span>
                  {item.description ? (
                    <span className="text-xs text-gray-500 dark:text-slate-400">
                      {item.description}
                    </span>
                  ) : null}
                </div>
              )}
            </>
          );
        }}
      </NavLink>
    );
  };

  return (
    <nav
      className={`bg-white dark:bg-slate-950 shadow-sm border-r border-gray-200/80 dark:border-slate-800 min-h-screen flex flex-col transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-72'
      }`}
      aria-label="Menu principal"
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
        <div className={isCollapsed ? 'flex flex-col items-center gap-2' : 'flex flex-col gap-3'}>
          <img
            src={isCollapsed ? sergioFrancoMark : sergioFrancoLogo}
            alt="Sérgio Franco Medicina Diagnóstica - Sistema de Agendamentos"
            className={isCollapsed ? 'h-12 w-12' : 'h-16 w-auto'}
            draggable={false}
          />
          {user ? (
            <span
              className={`text-xs font-medium text-gray-500 dark:text-slate-400 truncate ${
                isCollapsed ? 'text-center w-full' : ''
              }`}
            >
              {user.name}
            </span>
          ) : null}
        </div>
      </div>

      <div className={`flex-1 ${isCollapsed ? 'px-2' : 'px-4'} py-4 space-y-4 overflow-y-auto`}>
        {(['operacao', 'cadastros', 'administracao'] as NavigationGroupId[]).map((group) => {
          const items = groupedItems.get(group) ?? [];
          if (items.length === 0) {
            return null;
          }

          const isGroupCollapsed = collapsedGroups[group];

          return (
            <section key={group} aria-label={NAVIGATION_GROUP_LABELS[group]} className="space-y-2">
              <button
                type="button"
                onClick={() => toggleGroup(group)}
                className={`flex items-center ${
                  isCollapsed ? 'justify-center' : 'justify-between'
                } w-full text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-slate-400`}
                aria-expanded={!isGroupCollapsed}
              >
                {!isCollapsed && NAVIGATION_GROUP_LABELS[group]}
                {isCollapsed ? null : (
                  <span className="text-[0.65rem]">
                    {isGroupCollapsed ? 'Mostrar' : 'Ocultar'}
                  </span>
                )}
              </button>
              {!isGroupCollapsed && (
                <div className="space-y-2">
                  {items.map((item) => renderNavLink(item))}
                </div>
              )}
            </section>
          );
        })}
      </div>

      <div
        className={`border-t border-gray-100 dark:border-slate-800 ${
          isCollapsed ? 'px-2 py-4' : 'px-6 py-6'
        }`}
      >
        <button
          type="button"
          onClick={handleLogout}
          className={`w-full inline-flex items-center justify-center gap-2 rounded-lg border border-transparent bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-red-500 ${
            isCollapsed ? 'px-2 py-2 text-xs' : 'px-4 py-2 text-sm font-medium'
          }`}
        >
          <ArrowLeftOnRectangleIcon className="h-5 w-5" aria-hidden="true" />
          {!isCollapsed && 'Sair'}
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
