import assert from 'node:assert/strict';
import test, { describe } from 'node:test';
import { renderToStaticMarkup } from 'react-dom/server';
import type { FC } from 'react';
import {
  Outlet,
  Route,
  RouterProvider,
  createMemoryRouter,
  createRoutesFromElements,
} from 'react-router-dom';
import { PrivateRoute } from '../../components/PrivateRoute';
import { withRole } from '../../components/withRole';
import { Role } from '../../constants/roles';
import { AuthContext } from '../../contexts/AuthContext';
import { ThemeContext } from '../../contexts/ThemeContext';
import { DashboardRedirect } from '../../pages/DashboardRedirect';
import type { AuthContextType, User } from '../../types/auth';

const createAuthContextValue = (role: Role): AuthContextType => {
  const user: User = {
    id: 'user-id',
    name: role === Role.ADMIN ? 'Ana Admin' : 'Carlos Colaborador',
    email: role === Role.ADMIN ? 'admin@example.com' : 'colab@example.com',
    created_at: new Date().toISOString(),
    role: role === Role.ADMIN ? 'admin' : 'colaborador',
    is_admin: role === Role.ADMIN,
  };

  return {
    user,
    isLoading: false,
    isAuthenticated: true,
    login: async () => {},
    logout: async () => {},
    register: async () => {},
    refreshUser: async () => {},
  };
};

const themeValue = {
  theme: 'light' as const,
  setTheme: () => {},
  toggleTheme: () => {},
};

const OperationStub: FC = () => <p>Operacional</p>;
const AdminStub: FC = () => <p>Admin area</p>;

const ProtectedOperation = withRole([Role.COLABORADOR, Role.ADMIN])(OperationStub);
const ProtectedAdmin = withRole([Role.ADMIN])(AdminStub);

const TestLayout: FC = () => (
  <div>
    <Outlet />
  </div>
);

const renderRoute = (initialPath: string, role: Role) => {
  const router = createMemoryRouter(
    createRoutesFromElements(
      <Route
        element={
          <PrivateRoute>
            <TestLayout />
          </PrivateRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardRedirect />} />
        <Route path="/dashboard/operacao" element={<ProtectedOperation />} />
        <Route path="/dashboard/admin" element={<ProtectedAdmin />} />
        <Route path="/admin/usuarios" element={<ProtectedAdmin />} />
      </Route>
    ),
    {
      initialEntries: [initialPath],
    }
  );

  const markup = renderToStaticMarkup(
    <AuthContext.Provider value={createAuthContextValue(role)}>
      <ThemeContext.Provider value={themeValue}>
        <RouterProvider router={router} />
      </ThemeContext.Provider>
    </AuthContext.Provider>
  );

  return {
    markup: markup.replace(/\s+/g, ' ').trim(),
    location: router.state.location.pathname,
  };
};

describe('RBAC route guards', () => {
  test('colaborador redirecionado para dashboard operacional', () => {
    const result = renderRoute('/dashboard', Role.COLABORADOR);
    assert.ok(result.markup.includes('data-redirect-target'));
    assert.ok(result.markup.includes('/dashboard/operacao'));
  });

  test('colaborador bloqueado em rotas administrativas', () => {
    const result = renderRoute('/admin/usuarios', Role.COLABORADOR);
    assert.ok(result.markup.includes('Acesso restrito'));
  });

  test('administrador acessa rotas administrativas', () => {
    const result = renderRoute('/admin/usuarios', Role.ADMIN);
    assert.equal(result.location, '/admin/usuarios');
    assert.ok(result.markup.includes('Admin area'));
  });
});

