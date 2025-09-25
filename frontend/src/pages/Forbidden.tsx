import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import React, { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

export const ForbiddenPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const headingRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    headingRef.current?.focus();

    const timeout = window.setTimeout(() => {
      navigate('/dashboard', { replace: true });
    }, 4000);

    return () => window.clearTimeout(timeout);
  }, [navigate]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="max-w-lg w-full bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl p-8 shadow-sm text-center space-y-6">
        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 dark:bg-red-900/40">
          <ExclamationTriangleIcon className="h-8 w-8 text-red-600 dark:text-red-300" aria-hidden="true" />
        </div>
        <div className="space-y-2">
          <h1
            ref={headingRef}
            tabIndex={-1}
            className="text-2xl font-semibold text-gray-900 dark:text-slate-100 focus:outline-none"
          >
            Acesso não permitido
          </h1>
          <p className="text-gray-600 dark:text-slate-300">
            Você não possui permissão para acessar{' '}
            <span className="font-medium text-gray-900 dark:text-slate-100">
              {location.state?.from?.pathname ?? 'esta página'}
            </span>
            . Estamos redirecionando você para o dashboard.
          </p>
        </div>
        <button
          type="button"
          onClick={() => navigate('/dashboard', { replace: true })}
          className="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500 text-white text-sm font-medium"
        >
          Ir para o dashboard agora
        </button>
      </div>
    </div>
  );
};

export default ForbiddenPage;
