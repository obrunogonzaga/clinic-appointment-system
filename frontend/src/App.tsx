import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { HashRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Navigation } from './components/Navigation';
import { PrivateRoute } from './components/PrivateRoute';
import { ThemeProvider } from './contexts/ThemeContext';
import { AppointmentsPage } from './pages/AppointmentsPage';
import { CarsPage } from './pages/CarsPage';
import { CollectorsPage } from './pages/CollectorsPage';
import { Dashboard } from './pages/Dashboard';
import { DriverRoutePage } from './pages/DriverRoutePage';
import { DriversPage } from './pages/DriversPage';
import { Login } from './pages/Login';
import { Setup } from './pages/Setup';
import { UsersPage } from './pages/UsersPage';
import { PublicRegister } from './pages/PublicRegister';
import { VerifyEmail } from './pages/VerifyEmail';
import { TagsPage } from './pages/TagsPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function Shell() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isNavigationCollapsed, setIsNavigationCollapsed] = useState(false);
  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard onTabChange={setActiveTab} />;
      case 'appointments':
        return <AppointmentsPage />;
      case 'drivers':
        return <DriversPage />;
      case 'collectors':
        return <CollectorsPage />;
      case 'cars':
        return <CarsPage />;
      case 'users':
        return <UsersPage />;
      case 'tags':
        return <TagsPage />;
      default:
        return <Dashboard onTabChange={setActiveTab} />;
    }
  };
  return (
    <PrivateRoute>
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 flex transition-colors duration-300">
        <Navigation
          activeTab={activeTab}
          onTabChange={setActiveTab}
          isCollapsed={isNavigationCollapsed}
          onToggleCollapse={() =>
            setIsNavigationCollapsed((previousState) => !previousState)
          }
        />
        <main className="flex-1 p-8 transition-all duration-300">
          {renderContent()}
        </main>
      </div>
    </PrivateRoute>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
          <HashRouter>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<PublicRegister />} />
              <Route path="/setup" element={<Setup />} />
              <Route path="/verify-email" element={<VerifyEmail />} />
              <Route path="/verify-email/:token" element={<VerifyEmail />} />

              {/* Protected routes */}
              <Route path="/routes/driver" element={
                <PrivateRoute>
                  <DriverRoutePage />
                </PrivateRoute>
              } />
              <Route path="*" element={<Shell />} />
            </Routes>
          </HashRouter>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
