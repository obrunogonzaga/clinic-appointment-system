import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HashRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { PrivateRoute } from './components/PrivateRoute';
import { ThemeProvider } from './contexts/ThemeContext';
import { AppointmentsPage } from './pages/AppointmentsPage';
import { CarsPage } from './pages/CarsPage';
import { CollectorsPage } from './pages/CollectorsPage';
import { DriverRoutePage } from './pages/DriverRoutePage';
import { DriversPage } from './pages/DriversPage';
import { Login } from './pages/Login';
import { Setup } from './pages/Setup';
import { UsersPage } from './pages/UsersPage';
import { PublicRegister } from './pages/PublicRegister';
import { VerifyEmail } from './pages/VerifyEmail';
import { TagsPage } from './pages/TagsPage';
import { LogisticsPackagesPage } from './pages/LogisticsPackagesPage';
import { AppLayout } from './layouts/AppLayout';
import { DashboardRedirect } from './pages/dashboard/DashboardRedirect';
import { OperationDashboardPage } from './pages/dashboard/OperationDashboardPage';
import { AdminDashboardPage } from './pages/dashboard/AdminDashboardPage';
import { ForbiddenPage } from './pages/Forbidden';
import { withRole } from './components/rbac/withRole';
import { ROLES } from './constants/roles';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const OperationDashboardRoute = withRole([ROLES.COLABORADOR, ROLES.ADMIN])(OperationDashboardPage);
const AdminDashboardRoute = withRole([ROLES.ADMIN])(AdminDashboardPage);
const AppointmentsRoute = withRole([ROLES.COLABORADOR, ROLES.ADMIN])(AppointmentsPage);
const DriversRoute = withRole([ROLES.COLABORADOR, ROLES.ADMIN])(DriversPage);
const CollectorsRoute = withRole([ROLES.COLABORADOR, ROLES.ADMIN])(CollectorsPage);
const CarsRoute = withRole([ROLES.COLABORADOR, ROLES.ADMIN])(CarsPage);
const PackagesRoute = withRole([ROLES.COLABORADOR, ROLES.ADMIN])(LogisticsPackagesPage);
const UsersRoute = withRole([ROLES.ADMIN])(UsersPage);
const TagsRoute = withRole([ROLES.ADMIN])(TagsPage);

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
                path="/*"
                element={
                  <PrivateRoute>
                    <AppLayout />
                  </PrivateRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardRedirect />} />
                <Route path="dashboard/operacao" element={<OperationDashboardRoute />} />
                <Route path="dashboard/admin" element={<AdminDashboardRoute />} />
                <Route path="agendamentos" element={<AppointmentsRoute />} />
                <Route path="cadastros">
                  <Route path="motoristas" element={<DriversRoute />} />
                  <Route path="coletoras" element={<CollectorsRoute />} />
                  <Route path="carros" element={<CarsRoute />} />
                  <Route path="pacotes" element={<PackagesRoute />} />
                </Route>
                <Route path="admin">
                  <Route path="usuarios" element={<UsersRoute />} />
                  <Route path="tags" element={<TagsRoute />} />
                </Route>
                <Route path="403" element={<ForbiddenPage />} />
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
