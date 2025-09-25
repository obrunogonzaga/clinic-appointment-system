import React, { useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';

interface BreadcrumbItem {
  label: string;
  path: string;
  isCurrent: boolean;
}

const LABEL_MAP: Record<string, { label: string; path?: string }> = {
  dashboard: { label: 'Dashboard', path: '/dashboard' },
  operacao: { label: 'Operação', path: '/dashboard/operacao' },
  admin: { label: 'Administração', path: '/dashboard/admin' },
  agendamentos: { label: 'Agendamentos', path: '/agendamentos' },
  cadastros: { label: 'Cadastros' },
  motoristas: { label: 'Motoristas', path: '/cadastros/motoristas' },
  coletoras: { label: 'Coletoras', path: '/cadastros/coletoras' },
  carros: { label: 'Carros', path: '/cadastros/carros' },
  pacotes: { label: 'Pacotes', path: '/cadastros/pacotes' },
  usuarios: { label: 'Usuários', path: '/admin/usuarios' },
  tags: { label: 'Tags', path: '/admin/tags' },
  adminArea: { label: 'Administração', path: '/admin' },
};

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();

  const items = useMemo<BreadcrumbItem[]>(() => {
    const segments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [
      {
        label: 'Início',
        path: '/dashboard',
        isCurrent: segments.length === 0,
      },
    ];

    let accumulatedPath = '';

    segments.forEach((segment, index) => {
      accumulatedPath += `/${segment}`;
      const mapEntry = LABEL_MAP[segment] ?? {
        label: segment.charAt(0).toUpperCase() + segment.slice(1),
      };

      const path = mapEntry.path ?? accumulatedPath;

      breadcrumbs.push({
        label: mapEntry.label,
        path,
        isCurrent: index === segments.length - 1,
      });
    });

    return breadcrumbs;
  }, [location.pathname]);

  return (
    <nav className="flex" aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1 text-sm text-gray-500 dark:text-slate-400">
        {items.map((item, index) => (
          <li key={`${item.path}-${item.label}`} className="inline-flex items-center">
            {index !== 0 && <span className="mx-2 text-gray-300">/</span>}
            {item.isCurrent ? (
              <span className="font-medium text-gray-700 dark:text-slate-100" aria-current="page">
                {item.label}
              </span>
            ) : (
              <Link
                to={item.path}
                className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              >
                {item.label}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};
