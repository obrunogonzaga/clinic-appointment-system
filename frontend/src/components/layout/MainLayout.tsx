import React, { useEffect, useRef, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Breadcrumbs } from '../Breadcrumbs';
import { Navigation } from '../Navigation';

export const MainLayout: React.FC = () => {
  const [isNavigationCollapsed, setIsNavigationCollapsed] = useState(false);
  const mainContentRef = useRef<HTMLElement>(null);
  const location = useLocation();

  useEffect(() => {
    mainContentRef.current?.focus();
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 flex transition-colors duration-300">
      <Navigation
        isCollapsed={isNavigationCollapsed}
        onToggleCollapse={() => setIsNavigationCollapsed((previous) => !previous)}
      />
      <main
        ref={mainContentRef}
        className="flex-1 p-6 sm:p-8 lg:p-10 transition-all duration-300"
        tabIndex={-1}
      >
        <div className="flex flex-col gap-6">
          <Breadcrumbs />
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
