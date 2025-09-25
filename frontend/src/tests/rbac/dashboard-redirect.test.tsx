import '../setup/test-env';
import { strict as assert } from 'node:assert';
import test from 'node:test';
import { ROLES } from '../../constants/roles';
import { getDashboardDestination } from '../../pages/dashboard/DashboardRedirect';

test('dashboard colaborador redireciona para visão operacional', () => {
  assert.equal(getDashboardDestination(ROLES.COLABORADOR), '/dashboard/operacao');
});

test('dashboard admin redireciona para visão administrativa', () => {
  assert.equal(getDashboardDestination(ROLES.ADMIN), '/dashboard/admin');
});
