import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import type { Role } from '../constants/roles';
import { resolveUserRole } from '../utils/session';

interface WithRoleOptions {
  redirectTo?: string;
}

type ComponentType<P> = React.ComponentType<P>;

type WithRoleResult<P> = React.FC<P>;

export function withRole<P extends Record<string, unknown>>(
  Component: ComponentType<P>,
  allowedRoles: Role[],
  options: WithRoleOptions = {},
): WithRoleResult<P> {
  const { redirectTo = '/403' } = options;

  const RoleGuard: React.FC<P> = (props) => {
    const { user, isLoading } = useAuth();
    const location = useLocation();
    const role = resolveUserRole(user);

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-slate-950">
          <div className="text-center space-y-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" />
            <p className="text-gray-600 dark:text-slate-300">
              Carregando permissões...
            </p>
          </div>
        </div>
      );
    }

    if (!role || !allowedRoles.includes(role)) {
      return (
        <Navigate
          to={redirectTo}
          state={{ from: location }}
          replace
        />
      );
    }

    return <Component {...props} />;
  };

  RoleGuard.displayName = `withRole(${Component.displayName || Component.name || 'Component'})`;

  return RoleGuard;
}
