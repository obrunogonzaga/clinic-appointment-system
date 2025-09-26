import { ChevronRightIcon } from '@heroicons/react/24/outline';
import React from 'react';
import { matchPath, useLocation } from 'react-router-dom';
import { APP_ROUTES } from '../config/appRoutes';

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();

  const matchedRoute = APP_ROUTES.find((route) =>
    matchPath({ path: route.path, end: true }, location.pathname),
  );

  const crumbs = matchedRoute?.breadcrumb ?? [];

  if (crumbs.length === 0) {
    return null;
  }

  return (
    <nav className="flex items-center text-sm text-gray-500 dark:text-slate-400" aria-label="Breadcrumb">
      <ol className="flex items-center gap-2">
        {crumbs.map((label, index) => (
          <li key={label} className="flex items-center gap-2">
            <span
              className={`uppercase tracking-wide ${
                index === crumbs.length - 1
                  ? 'font-semibold text-gray-700 dark:text-slate-200'
                  : 'text-gray-500 dark:text-slate-400'
              }`}
            >
              {label}
            </span>
            {index < crumbs.length - 1 ? (
              <ChevronRightIcon className="h-4 w-4" aria-hidden="true" />
            ) : null}
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
