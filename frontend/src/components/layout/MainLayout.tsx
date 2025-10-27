import React, { useEffect, useRef, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Bars3Icon } from '@heroicons/react/24/outline';
import { Breadcrumbs } from '../Breadcrumbs';
import { Navigation } from '../Navigation';
import sergioFrancoMark from '../../assets/sergio-franco-mark.svg';

export const MainLayout: React.FC = () => {
  const [isNavigationCollapsed, setIsNavigationCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const mainContentRef = useRef<HTMLElement>(null);
  const location = useLocation();

  useEffect(() => {
    mainContentRef.current?.focus();
  }, [location.pathname]);

  // Close mobile menu when location changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 transition-colors duration-300">
      {/* Mobile Header - Fixed at top */}
      <header className="lg:hidden fixed top-0 left-0 right-0 z-30 bg-white dark:bg-slate-950 border-b border-gray-200 dark:border-slate-800 px-4 py-3 shadow-sm">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setIsMobileMenuOpen(true)}
            className="p-2 -ml-2 rounded-md text-gray-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-900 hover:text-gray-900 dark:hover:text-slate-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-slate-950"
            aria-label="Abrir menu"
            aria-expanded={isMobileMenuOpen}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>

          {/* Logo no center */}
          <img
            src={sergioFrancoMark}
            alt="Sérgio Franco Medicina Diagnóstica"
            className="h-8 w-8"
            draggable={false}
          />

          {/* Spacer for balance */}
          <div className="w-10" />
        </div>
      </header>

      {/* Mobile Menu Backdrop */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Desktop & Mobile Layout */}
      <div className="flex min-h-screen lg:pt-0 pt-14">
        {/* Navigation - Desktop sidebar / Mobile drawer */}
        <div
          className={`
            fixed lg:static
            inset-y-0 left-0 z-50
            transform lg:transform-none
            transition-transform duration-300 ease-in-out
            ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
            pt-14 lg:pt-0
          `}
        >
          <Navigation
            isCollapsed={isNavigationCollapsed}
            onToggleCollapse={() => setIsNavigationCollapsed((previous) => !previous)}
            onMobileMenuClose={() => setIsMobileMenuOpen(false)}
          />
        </div>

        {/* Main Content */}
        <main
          ref={mainContentRef}
          className="flex-1 p-4 md:p-6 lg:p-10 transition-all duration-300 overflow-y-auto"
          tabIndex={-1}
        >
          <div className="flex flex-col gap-4 md:gap-6">
            <Breadcrumbs />
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
