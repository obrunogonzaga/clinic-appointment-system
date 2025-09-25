import type { ComponentType } from 'react';
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import type { Role } from '../../constants/roles';
import { ROLES } from '../../constants/roles';
import { useAuth } from '../../hooks/useAuth';
import { getUserRole } from '../../utils/session';

interface LoadingFallbackProps {
  message?: string;
}

const LoadingFallback: React.FC<LoadingFallbackProps> = ({ message }) => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-slate-950">
    <div className="text-center" role="status" aria-live="polite">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto" />
      <p className="mt-3 text-gray-600 dark:text-slate-300 text-sm font-medium">
        {message ?? 'Carregando permissões...'}
      </p>
    </div>
  </div>
);

export function withRole<P extends Record<string, unknown>>(
  allowedRoles: Role[],
) {
  return (WrappedComponent: ComponentType<P>): React.FC<P> => {
    const RoleGuard: React.FC<P> = (props) => {
      const { user, isLoading } = useAuth();
      const location = useLocation();

      if (isLoading) {
        return <LoadingFallback message="Verificando permissões" />;
      }

      const role = getUserRole(user);

      if (!allowedRoles.includes(role)) {
        const fallbackTarget = allowedRoles.includes(ROLES.ADMIN)
          ? '/dashboard'
          : '/dashboard';

        return (
          <Navigate
            to="/403"
            state={{ from: location.pathname, fallbackTarget }}
            replace
          />
        );
      }

      return <WrappedComponent {...(props as P)} />;
    };

    RoleGuard.displayName = `withRole(${WrappedComponent.displayName ?? WrappedComponent.name ?? 'Component'})`;

    return RoleGuard;
  };
}
