import React from 'react';
import { Navigate } from 'react-router-dom';
import { ROLES, type Role } from '../../constants/roles';
import { useAuth } from '../../hooks/useAuth';
import { getUserRole } from '../../utils/session';

export const getDashboardDestination = (role: Role): string =>
  role === ROLES.ADMIN ? '/dashboard/admin' : '/dashboard/operacao';

export const DashboardRedirect: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center" role="status" aria-live="polite">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-b-2 border-blue-600" />
          <p className="mt-2 text-sm text-gray-600 dark:text-slate-300">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  const role = getUserRole(user);
  const target = getDashboardDestination(role);

  return <Navigate to={target} replace />;
};
