import { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface ForbiddenProps {
  redirectPath?: string;
  message?: string;
  heading?: string;
  redirectDelayMs?: number;
}

export const Forbidden: React.FC<ForbiddenProps> = ({
  redirectPath = '/dashboard',
  heading = 'Acesso não autorizado',
  message = 'Você não tem permissão para acessar este conteúdo.',
  redirectDelayMs = 2500,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const headingRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    headingRef.current?.focus();
  }, []);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      navigate(redirectPath, {
        replace: true,
        state: { from: location.pathname },
      });
    }, redirectDelayMs);

    return () => window.clearTimeout(timeout);
  }, [navigate, redirectPath, redirectDelayMs, location.pathname]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center" role="alert">
      <div className="max-w-xl w-full bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl shadow-sm p-8 text-center">
        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 dark:bg-red-500/10 mb-4">
          <span className="text-3xl" aria-hidden="true">
            🚫
          </span>
        </div>
        <h1
          ref={headingRef}
          className="text-2xl font-semibold text-gray-900 dark:text-slate-100"
          tabIndex={-1}
        >
          {heading}
        </h1>
        <p className="mt-3 text-gray-600 dark:text-slate-300">{message}</p>
        <p className="mt-2 text-sm text-gray-500 dark:text-slate-400">
          Você será redirecionado automaticamente para o dashboard.
        </p>
        <button
          type="button"
          className="mt-6 inline-flex items-center justify-center px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium shadow hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500"
          onClick={() =>
            navigate(redirectPath, {
              replace: true,
              state: { from: location.pathname },
            })
          }
        >
          Ir para o dashboard
        </button>
      </div>
    </div>
  );
};

