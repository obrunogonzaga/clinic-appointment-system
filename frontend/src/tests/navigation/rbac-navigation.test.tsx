import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import test, { describe } from 'node:test';
import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { Navigation } from '../../components/Navigation';
import { Role } from '../../constants/roles';
import { AuthContext } from '../../contexts/AuthContext';
import { ThemeContext } from '../../contexts/ThemeContext';
import type { AuthContextType, User } from '../../types/auth';

const createUser = (role: Role): User => ({
  id: 'user-id',
  name: role === Role.ADMIN ? 'Ana Admin' : 'Carlos Colaborador',
  email: role === Role.ADMIN ? 'admin@example.com' : 'colab@example.com',
  created_at: new Date().toISOString(),
  role: role === Role.ADMIN ? 'admin' : 'colaborador',
  is_admin: role === Role.ADMIN,
});

const renderSidebar = (role: Role): string => {
  const user = createUser(role);

  const authContextValue: AuthContextType = {
    user,
    isLoading: false,
    isAuthenticated: true,
    login: async () => {},
    logout: async () => {},
    register: async () => {},
    refreshUser: async () => {},
  };

  const themeValue = {
    theme: 'light' as const,
    setTheme: () => {},
    toggleTheme: () => {},
  };

  const markup = renderToStaticMarkup(
    <MemoryRouter initialEntries={['/dashboard']}>
      <AuthContext.Provider value={authContextValue}>
        <ThemeContext.Provider value={themeValue}>
          <Navigation role={role} isCollapsed={false} onToggleCollapse={() => {}} />
        </ThemeContext.Provider>
      </AuthContext.Provider>
    </MemoryRouter>
  );

  return markup.replace(/\s+/g, ' ').trim();
};

const snapshotHash = (markup: string): string =>
  createHash('sha256').update(markup).digest('hex');

describe('Navigation RBAC', () => {
  test('colaborador não visualiza itens administrativos', () => {
    const markup = renderSidebar(Role.COLABORADOR);
    assert.ok(!markup.includes('Administração'));
  });

  test('administrador visualiza itens administrativos', () => {
    const markup = renderSidebar(Role.ADMIN);
    assert.ok(markup.includes('Administração'));
  });

  test('snapshot colaborador', () => {
    const markup = renderSidebar(Role.COLABORADOR);
    assert.equal(snapshotHash(markup), 'f5dc60efe2d6b17185cef2462895ae0b3ad03971cf60ee067edde808a012887e');
  });

  test('snapshot administrador', () => {
    const markup = renderSidebar(Role.ADMIN);
    assert.equal(snapshotHash(markup), 'beb109065fddd2d7c90bd6dd9ffc94645a50dad34aa06f022619a91339a3de87');
  });
});

