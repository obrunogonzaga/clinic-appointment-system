import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { HashRouter, Navigate, Route, Routes } from 'react-router-dom';
import { APP_ROUTES } from './config/appRoutes';
import MainLayout from './components/layout/MainLayout';
import { PrivateRoute } from './components/PrivateRoute';
import { withRole } from './components/withRole';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { useAuth } from './hooks/useAuth';
import { PublicRegister } from './pages/PublicRegister';
import { DriverRoutePage } from './pages/DriverRoutePage';
import { ForbiddenPage } from './pages/Forbidden';
import { Login } from './pages/Login';
import { Setup } from './pages/Setup';
import { VerifyEmail } from './pages/VerifyEmail';
import { ROLES } from './constants/roles';
import { resolveUserRole } from './utils/session';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

const DashboardRedirect: React.FC = () => {
  const { user } = useAuth();
  const role = resolveUserRole(user);

  if (!role) {
    return <Navigate to="/login" replace />;
  }

  const target = role === ROLES.ADMIN ? '/dashboard/admin' : '/dashboard/operacao';
  return <Navigate to={target} replace />;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
          <HashRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<PublicRegister />} />
              <Route path="/setup" element={<Setup />} />
              <Route path="/verify-email" element={<VerifyEmail />} />
              <Route path="/verify-email/:token" element={<VerifyEmail />} />

              <Route
                path="/routes/driver"
                element={
                  <PrivateRoute>
                    <DriverRoutePage />
                  </PrivateRoute>
                }
              />

              <Route
                element={
                  <PrivateRoute>
                    <MainLayout />
                  </PrivateRoute>
                }
              >
                <Route path="/dashboard" element={<DashboardRedirect />} />
                {APP_ROUTES.map((route) => {
                  const GuardedComponent = withRole(route.Component, route.allowedRoles);
                  return (
                    <Route
                      key={route.id}
                      path={route.path}
                      element={<GuardedComponent />}
                    />
                  );
                })}
                <Route path="/403" element={<ForbiddenPage />} />
              </Route>

              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </HashRouter>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
