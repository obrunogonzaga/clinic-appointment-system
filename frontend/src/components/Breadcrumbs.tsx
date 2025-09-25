import { Fragment } from 'react';
import { Link, useLocation } from 'react-router-dom';

const LABEL_MAP: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/dashboard/operacao': 'Dashboard Operacional',
  '/dashboard/admin': 'Dashboard Administrativo',
  '/agendamentos': 'Agendamentos',
  '/cadastros': 'Cadastros',
  '/cadastros/motoristas': 'Motoristas',
  '/cadastros/coletoras': 'Coletoras',
  '/cadastros/carros': 'Carros',
  '/cadastros/pacotes': 'Pacotes Logísticos',
  '/admin': 'Administração',
  '/admin/usuarios': 'Usuários',
  '/admin/tags': 'Tags',
};

const buildSegments = (pathname: string): string[] => {
  const segments = pathname.split('/').filter(Boolean);

  if (segments.length === 0) {
    return ['/dashboard'];
  }

  const breadcrumbs: string[] = [];
  let current = '';

  segments.forEach((segment) => {
    current = `${current}/${segment}`;
    breadcrumbs.push(current);
  });

  return breadcrumbs;
};

const resolveLabel = (path: string): string => {
  return LABEL_MAP[path] ?? path.split('/').pop()?.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()) ?? path;
};

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const segments = buildSegments(location.pathname);

  if (segments.length <= 1 && segments[0] === '/dashboard') {
    return null;
  }

  return (
    <nav className="text-sm text-gray-500 dark:text-slate-400" aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2" role="list">
        <li>
          <Link
            to="/dashboard"
            className="hover:text-blue-600 dark:hover:text-blue-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
          >
            Início
          </Link>
        </li>
        {segments.map((segment, index) => (
          <Fragment key={segment}>
            <li aria-hidden="true">/</li>
            <li>
              {index === segments.length - 1 ? (
                <span className="text-gray-700 dark:text-slate-200" aria-current="page">
                  {resolveLabel(segment)}
                </span>
              ) : (
                <Link
                  to={segment}
                  className="hover:text-blue-600 dark:hover:text-blue-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
                >
                  {resolveLabel(segment)}
                </Link>
              )}
            </li>
          </Fragment>
        ))}
      </ol>
    </nav>
  );
};

