import '../setup/test-env';
import { strict as assert } from 'node:assert';
import test from 'node:test';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { Navigation } from '../../components/Navigation';
import { AuthContext } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import type { AuthContextType, User } from '../../types/auth';

const createAuthContextValue = (overrides: Partial<AuthContextType>): AuthContextType => ({
  user: null,
  isLoading: false,
  isAuthenticated: true,
  login: async () => {},
  logout: async () => {},
  register: async () => {},
  refreshUser: async () => {},
  ...overrides,
});

const renderNavigation = (user: User) =>
  renderToStaticMarkup(
    <AuthContext.Provider value={createAuthContextValue({ user })}>
      <ThemeProvider>
        <MemoryRouter initialEntries={[user.is_admin ? '/dashboard/admin' : '/dashboard/operacao']}>
          <Navigation isCollapsed={false} onToggleCollapse={() => {}} />
        </MemoryRouter>
      </ThemeProvider>
    </AuthContext.Provider>,
  );

test('colaboradores não visualizam seções administrativas na sidebar', () => {
  const html = renderNavigation({
    id: '1',
    email: 'colaborador@example.com',
    name: 'Colaborador',
    created_at: new Date().toISOString(),
    role: 'colaborador',
    is_admin: false,
  });

  assert.ok(html.includes('Operação'));
  assert.ok(html.includes('Cadastros'));
  assert.ok(!html.includes('Administração'));
  assert.ok(!html.includes('Usuários'));
});

test('administradores visualizam menu de administração completo', () => {
  const html = renderNavigation({
    id: '2',
    email: 'admin@example.com',
    name: 'Admin',
    created_at: new Date().toISOString(),
    role: 'admin',
    is_admin: true,
  });

  assert.ok(html.includes('Administração'));
  assert.ok(html.includes('Usuários'));
  assert.ok(html.includes('Tags'));
});
