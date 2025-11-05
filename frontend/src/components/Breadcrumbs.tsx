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

  // Mobile: show only current page, Desktop: show full breadcrumb
  const displayCrumbs = crumbs;

  return (
    <nav className="flex items-center text-xs md:text-sm text-gray-500 dark:text-slate-400" aria-label="Breadcrumb">
      {/* Mobile: Only show current page */}
      <div className="block md:hidden">
        <span className="font-semibold text-gray-700 dark:text-slate-200 uppercase tracking-wide">
          {crumbs[crumbs.length - 1]}
        </span>
      </div>

      {/* Desktop: Show full breadcrumb */}
      <ol className="hidden md:flex items-center gap-2">
        {displayCrumbs.map((label, index) => (
          <li key={label} className="flex items-center gap-2">
            <span
              className={`uppercase tracking-wide ${
                index === displayCrumbs.length - 1
                  ? 'font-semibold text-gray-700 dark:text-slate-200'
                  : 'text-gray-500 dark:text-slate-400'
              }`}
            >
              {label}
            </span>
            {index < displayCrumbs.length - 1 ? (
              <ChevronRightIcon className="h-4 w-4" aria-hidden="true" />
            ) : null}
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
