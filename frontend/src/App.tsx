import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HashRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { PrivateRoute } from './components/PrivateRoute';
import { withRole } from './components/withRole';
import { Role } from './constants/roles';
import { ThemeProvider } from './contexts/ThemeContext';
import { AppLayout } from './layouts/AppLayout';
import { AppointmentsPage } from './pages/AppointmentsPage';
import { CarsPage } from './pages/CarsPage';
import { CollectorsPage } from './pages/CollectorsPage';
import { DashboardRedirect } from './pages/DashboardRedirect';
import { DriverRoutePage } from './pages/DriverRoutePage';
import { DriversPage } from './pages/DriversPage';
import { Login } from './pages/Login';
import { Setup } from './pages/Setup';
import { UsersPage } from './pages/UsersPage';
import { PublicRegister } from './pages/PublicRegister';
import { VerifyEmail } from './pages/VerifyEmail';
import { TagsPage } from './pages/TagsPage';
import { LogisticsPackagesPage } from './pages/LogisticsPackagesPage';
import { OperationDashboard } from './pages/dashboards/OperationDashboard';
import { AdminDashboard } from './pages/dashboards/AdminDashboard';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const OperationDashboardPage = withRole([Role.COLABORADOR, Role.ADMIN])(OperationDashboard);
const AdminDashboardPage = withRole([Role.ADMIN])(AdminDashboard);
const AppointmentsProtectedPage = withRole([Role.COLABORADOR, Role.ADMIN])(AppointmentsPage);
const DriversProtectedPage = withRole([Role.COLABORADOR, Role.ADMIN])(DriversPage);
const CollectorsProtectedPage = withRole([Role.COLABORADOR, Role.ADMIN])(CollectorsPage);
const CarsProtectedPage = withRole([Role.COLABORADOR, Role.ADMIN])(CarsPage);
const LogisticsProtectedPage = withRole([Role.COLABORADOR, Role.ADMIN])(LogisticsPackagesPage);
const UsersAdminPage = withRole([Role.ADMIN])(UsersPage);
const TagsAdminPage = withRole([Role.ADMIN])(TagsPage);

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
              <Route
                element={
                  <PrivateRoute>
                    <AppLayout />
                  </PrivateRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<DashboardRedirect />} />
                <Route path="/dashboard/operacao" element={<OperationDashboardPage />} />
                <Route path="/dashboard/admin" element={<AdminDashboardPage />} />
                <Route path="/agendamentos" element={<AppointmentsProtectedPage />} />
                <Route path="/cadastros/motoristas" element={<DriversProtectedPage />} />
                <Route path="/cadastros/coletoras" element={<CollectorsProtectedPage />} />
                <Route path="/cadastros/carros" element={<CarsProtectedPage />} />
                <Route path="/cadastros/pacotes" element={<LogisticsProtectedPage />} />
                <Route path="/admin/usuarios" element={<UsersAdminPage />} />
                <Route path="/admin/tags" element={<TagsAdminPage />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Route>
            </Routes>
          </HashRouter>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
