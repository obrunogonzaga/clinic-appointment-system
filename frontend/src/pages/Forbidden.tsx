import React, { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const REDIRECT_DELAY = 4000;

interface ForbiddenLocationState {
  from?: string;
  fallbackTarget?: string;
}

export const ForbiddenPage: React.FC = () => {
  const headingRef = useRef<HTMLHeadingElement>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as ForbiddenLocationState | null;
  const fallbackTarget = state?.fallbackTarget ?? '/dashboard';

  useEffect(() => {
    if (typeof window !== 'undefined') {
      headingRef.current?.focus();
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    const timeout = window.setTimeout(() => {
      navigate(fallbackTarget, { replace: true });
    }, REDIRECT_DELAY);

    return () => window.clearTimeout(timeout);
  }, [fallbackTarget, navigate]);

  return (
    <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
      <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-red-100 text-red-600">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M12 9v3m0 3h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L4.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <div role="alert" aria-live="assertive" className="space-y-3 max-w-md">
        <h1
          ref={headingRef}
          tabIndex={-1}
          className="text-2xl font-semibold text-gray-900 dark:text-slate-100"
        >
          Acesso não autorizado
        </h1>
        <p className="text-gray-600 dark:text-slate-300">
          Você não tem permissão para acessar
          {state?.from ? ` “${state.from}”` : ' este conteúdo'} com o seu papel atual.
        </p>
        <p className="text-sm text-gray-500 dark:text-slate-400">
          Você será redirecionado automaticamente para o seu dashboard padrão em alguns segundos.
        </p>
        <button
          type="button"
          onClick={() => navigate(fallbackTarget, { replace: true })}
          className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
        >
          Ir agora para o dashboard
        </button>
      </div>
    </div>
  );
};
