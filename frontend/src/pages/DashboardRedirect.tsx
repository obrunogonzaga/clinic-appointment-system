import { useEffect, useRef } from 'react';
import { Navigate } from 'react-router-dom';
import { Role } from '../constants/roles';
import { useAuth } from '../hooks/useAuth';
import { resolveUserRole } from '../utils/roleUtils';

export const DashboardRedirect: React.FC = () => {
  const { user, isLoading } = useAuth();
  const focusRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    if (!isLoading) {
      focusRef.current?.focus();
    }
  }, [isLoading]);

  if (isLoading) {
    return (
      <div className="min-h-[40vh] flex flex-col items-center justify-center gap-3" role="status">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <p ref={focusRef} className="text-gray-600 dark:text-slate-300" tabIndex={-1}>
          Preparando seu dashboard...
        </p>
      </div>
    );
  }

  const role = resolveUserRole(user);
  const targetPath = role === Role.ADMIN ? '/dashboard/admin' : '/dashboard/operacao';

  return (
    <>
      <span className="sr-only" data-redirect-target>
        Redirecionando para {targetPath}
      </span>
      <Navigate to={targetPath} replace />
    </>
  );
};

