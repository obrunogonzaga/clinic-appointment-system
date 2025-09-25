import type { AuthContextType, User } from '../../types/auth';

const assert = require('node:assert/strict');
const { describe, test } = require('node:test');
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const { MemoryRouter } = require('react-router-dom');

const noop = () => undefined;

(globalThis as unknown as { window: unknown }).window = {
  ENV: {
    API_URL: 'http://localhost:8000',
  },
  matchMedia: () => ({
    matches: false,
    addEventListener: noop,
    removeEventListener: noop,
  }),
  localStorage: {
    getItem: () => null,
    setItem: noop,
  },
  location: {
    href: 'http://localhost/',
  },
};

(globalThis as unknown as { import_meta: unknown }).import_meta = {
  env: {
    VITE_API_URL: 'http://localhost:8000',
  },
};

(globalThis as unknown as { document: unknown }).document = {
  documentElement: {
    classList: {
      add: noop,
      remove: noop,
    },
  },
};

const { Navigation } = require('../../components/Navigation');
const { AuthContext } = require('../../contexts/AuthContext');
const { ThemeContext } = require('../../contexts/ThemeContext');

const buildAuthContext = (user: User | null): AuthContextType => ({
  user,
  isLoading: false,
  isAuthenticated: !!user,
  login: async () => undefined,
  logout: async () => undefined,
  register: async () => undefined,
  refreshUser: async () => undefined,
});

const themeContextValue = {
  theme: 'light' as const,
  setTheme: () => undefined,
  toggleTheme: () => undefined,
};

const renderNavigationForUser = (user: User | null) =>
  renderToStaticMarkup(
    React.createElement(
      AuthContext.Provider,
      { value: buildAuthContext(user) },
      React.createElement(
        ThemeContext.Provider,
        { value: themeContextValue },
        React.createElement(
          MemoryRouter,
          { initialEntries: [user?.is_admin ? '/admin/usuarios' : '/dashboard/operacao'] },
          React.createElement(Navigation, { isCollapsed: false, onToggleCollapse: () => undefined }),
        ),
      ),
    ),
  );

describe('Navigation RBAC', () => {
  test('collaborator does not see administrative links', () => {
    const collaboratorNav = renderNavigationForUser({
      id: '1',
      email: 'colab@example.com',
      name: 'Colaborador',
      created_at: new Date().toISOString(),
      is_admin: false,
      role: 'colaborador',
    });

    assert.ok(collaboratorNav.includes('Operação'));
    assert.ok(collaboratorNav.includes('Agendamentos'));
    assert.equal(collaboratorNav.includes('Administração'), false);
    assert.equal(collaboratorNav.includes('Usuários'), false);
  });

  test('admin sees administrative links', () => {
    const adminNav = renderNavigationForUser({
      id: '2',
      email: 'admin@example.com',
      name: 'Admin',
      created_at: new Date().toISOString(),
      is_admin: true,
      role: 'admin',
    });

    assert.ok(adminNav.includes('Administração'));
    assert.ok(adminNav.includes('Usuários'));
    assert.ok(adminNav.includes('Tags'));
  });
});
