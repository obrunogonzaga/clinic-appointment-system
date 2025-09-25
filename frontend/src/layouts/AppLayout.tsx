import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Breadcrumbs } from '../components/Breadcrumbs';
import { Navigation } from '../components/Navigation';
import { useAuth } from '../hooks/useAuth';
import { resolveUserRole } from '../utils/roleUtils';

export const AppLayout: React.FC = () => {
  const { user } = useAuth();
  const [isNavigationCollapsed, setIsNavigationCollapsed] = useState(false);

  const role = resolveUserRole(user);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 flex transition-colors duration-300">
      <Navigation
        role={role}
        isCollapsed={isNavigationCollapsed}
        onToggleCollapse={() => setIsNavigationCollapsed((previous) => !previous)}
      />
      <main className="flex-1 p-6 md:p-8 transition-all duration-300" role="main">
        <div className="flex flex-col gap-4">
          <Breadcrumbs />
          <div className="bg-white dark:bg-slate-950 border border-gray-200 dark:border-slate-800 rounded-2xl shadow-sm p-4 md:p-6">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
};

