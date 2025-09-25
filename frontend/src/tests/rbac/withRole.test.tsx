import '../setup/test-env';
import { strict as assert } from 'node:assert';
import test from 'node:test';
import { ROLES } from '../../constants/roles';
import { userHasRole } from '../../utils/session';
import type { User } from '../../types/auth';

const buildUser = (overrides: Partial<User>): User => ({
  id: overrides.id ?? 'user',
  email: overrides.email ?? 'user@example.com',
  name: overrides.name ?? 'Usuário',
  created_at: overrides.created_at ?? new Date().toISOString(),
  role: overrides.role,
  is_admin: overrides.is_admin,
});

test('colaborador não possui acesso a rotas exclusivas de admin', () => {
  const collaborator = buildUser({ role: 'colaborador', is_admin: false });
  assert.equal(userHasRole(collaborator, [ROLES.ADMIN]), false);
});

test('admin possui acesso às rotas compartilhadas', () => {
  const admin = buildUser({ role: 'admin', is_admin: true });
  assert.equal(userHasRole(admin, [ROLES.COLABORADOR, ROLES.ADMIN]), true);
});
