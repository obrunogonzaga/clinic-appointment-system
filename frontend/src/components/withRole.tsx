import type { ComponentType } from 'react';
import { useMemo } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Role } from '../constants/roles';
import { useAuth } from '../hooks/useAuth';
import { resolveUserRole } from '../utils/roleUtils';
import { Forbidden } from './Forbidden';

interface TelemetryEvent {
  name: string;
  properties?: Record<string, unknown>;
}

const emitTelemetry = (event: TelemetryEvent) => {
  if (typeof window !== 'undefined' && window?.analytics?.track) {
    window.analytics.track(event.name, event.properties ?? {});
    return;
  }

  if (typeof console !== 'undefined') {
    console.info(`[telemetry] ${event.name}`, event.properties ?? {});
  }
};

export const withRole = <Props extends object>(allowedRoles: Role[]) => {
  return (WrappedComponent: ComponentType<Props>) => {
    const RoleGuard = (props: Props) => {
      const { user, isLoading } = useAuth();
      const location = useLocation();

      const resolvedRole = useMemo(() => resolveUserRole(user), [user]);

      if (isLoading) {
        return (
          <div className="min-h-[60vh] flex items-center justify-center" role="status">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto" />
              <p className="mt-3 text-gray-600 dark:text-slate-300">
                Carregando permissões...
              </p>
            </div>
          </div>
        );
      }

      if (!user || !resolvedRole) {
        return (
          <Navigate
            to="/login"
            replace
            state={{ from: location }}
          />
        );
      }

      if (!allowedRoles.includes(resolvedRole)) {
        emitTelemetry({
          name: 'rbac_access_blocked',
          properties: {
            attemptedPath: location.pathname,
            role: resolvedRole,
          },
        });

        return (
          <Forbidden
            heading="Acesso restrito"
            message="Este conteúdo é exclusivo para outro perfil de acesso."
          />
        );
      }

      return <WrappedComponent {...props} />;
    };

    RoleGuard.displayName = `withRole(${WrappedComponent.displayName ?? WrappedComponent.name ?? 'Component'})`;

    return RoleGuard;
  };
};

