import React, { useEffect, useRef, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Navigation } from '../components/Navigation';
import { Breadcrumbs } from '../components/ui/Breadcrumbs';

export const AppLayout: React.FC = () => {
  const [isNavigationCollapsed, setIsNavigationCollapsed] = useState(false);
  const mainContentRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

  useEffect(() => {
    if (mainContentRef.current) {
      mainContentRef.current.focus();
    }
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 flex transition-colors duration-300">
      <Navigation
        isCollapsed={isNavigationCollapsed}
        onToggleCollapse={() =>
          setIsNavigationCollapsed((previousState) => !previousState)
        }
      />
      <div className="flex-1 flex flex-col">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-800 bg-white/70 dark:bg-slate-950/60 backdrop-blur">
          <Breadcrumbs />
        </div>
        <div
          ref={mainContentRef}
          tabIndex={-1}
          className="flex-1 px-6 py-6 focus:outline-none"
          aria-live="polite"
        >
          <Outlet />
        </div>
      </div>
    </div>
  );
};
